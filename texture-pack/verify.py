"""Validate the released texture-only RT64 pack without extracting or installing it."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct
import sys
import zipfile
import zlib

import zstandard


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_entry(archive, raw_file, entry):
    if entry.compress_type == 93:
        raw_file.seek(entry.header_offset)
        header = raw_file.read(30)
        require(header[:4] == b"PK\x03\x04", f"Bad ZIP header: {entry.filename}")
        name_length, extra_length = struct.unpack_from("<HH", header, 26)
        raw_file.seek(name_length + extra_length, 1)
        compressed = raw_file.read(entry.compress_size)
        data = zstandard.ZstdDecompressor().decompress(
            compressed, max_output_size=entry.file_size
        )
    else:
        data = archive.read(entry)
    require(len(data) == entry.file_size, f"Size mismatch: {entry.filename}")
    require(zlib.crc32(data) == entry.CRC, f"CRC mismatch: {entry.filename}")
    return data


def verify_dds(data, name):
    require(len(data) >= 148 and data[:4] == b"DDS ", f"Invalid DDS: {name}")
    header_size, flags, height, width, pitch, depth, mip_count = struct.unpack_from(
        "<7I", data, 4
    )
    require(header_size == 124 and width > 0 and height > 0, f"Bad DDS size: {name}")
    require(data[84:88] == b"DX10", f"Missing DX10 header: {name}")
    pixel_format, dimension, misc, array_size, misc_alpha = struct.unpack_from(
        "<5I", data, 128
    )
    require(pixel_format == 98 and dimension == 3 and array_size == 1,
            f"Expected a single BC7_UNORM 2D texture: {name}")
    require(mip_count == max(width, height).bit_length(), f"Incomplete mip chain: {name}")
    expected_bytes = 148
    for level in range(mip_count):
        mip_width = max(1, width >> level)
        mip_height = max(1, height >> level)
        expected_bytes += ((mip_width + 3) // 4) * ((mip_height + 3) // 4) * 16
    require(len(data) == expected_bytes, f"Truncated or oversized mip data: {name}")


def verify(path, manifest):
    require(path.stat().st_size == manifest["bytes"], "Archive byte size differs from manifest")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    require(digest == manifest["sha256"], "Archive SHA-256 differs from manifest")
    with zipfile.ZipFile(path) as archive, path.open("rb") as raw_file:
        entries = archive.infolist()
        names = {entry.filename for entry in entries}
        require(len(entries) == len(names) == manifest["archive_entries"],
                "Duplicate or unexpected archive entries")
        expected_metadata = {"mod.json", "README.txt", "rt64.json", "rt64-low-mip-cache.bin"}
        require(expected_metadata <= names, "Required metadata/cache missing")
        dds_names = {name for name in names if name.endswith(".dds")}
        require(names == dds_names | expected_metadata, "Unexpected non-texture payload")
        require(len(dds_names) == manifest["dds_images"], "DDS count differs from manifest")
        metadata = {}
        for entry in entries:
            relative = PurePosixPath(entry.filename)
            require(not relative.is_absolute() and ".." not in relative.parts
                    and "\\" not in entry.filename, f"Unsafe path: {entry.filename}")
            data = read_entry(archive, raw_file, entry)
            if entry.filename in dds_names:
                require(relative.parts[0] == "textures", "DDS outside textures directory")
                verify_dds(data, entry.filename)
            elif entry.filename.endswith(".json"):
                metadata[entry.filename] = json.loads(data)
            elif entry.filename == "rt64-low-mip-cache.bin":
                require(len(data) > 0, "Empty low-mip cache")
        mod = metadata["mod.json"]
        require(mod["id"] == manifest["mod_id"] and mod["game_id"] == manifest["game_id"],
                "Wrong mod or game ID")
        require(mod["version"] == manifest["version"], "Wrong mod version")
        database = metadata["rt64.json"]
        require(database["configuration"]["hashVersion"] == manifest["hash_version"],
                "Unexpected RT64 hash version")
        require(len(database["textures"]) == manifest["mapping_count"], "Wrong mapping count")
        hashes = set()
        referenced = set()
        for binding in database["textures"]:
            texture_hash = binding["hashes"]["rt64"]
            require(re.fullmatch(r"[0-9a-f]{16}", texture_hash) is not None,
                    f"Invalid RT64 hash: {texture_hash}")
            require(texture_hash not in hashes, f"Duplicate RT64 hash: {texture_hash}")
            hashes.add(texture_hash)
            texture_name = binding["path"] + ".dds"
            require(texture_name in dds_names, f"Missing replacement: {texture_name}")
            referenced.add(texture_name)
        require(referenced == dds_names, "Unreferenced DDS textures")
    print(f"Verified {path.name}: {manifest['mapping_count']:,} mappings, "
          f"{manifest['dds_images']:,} BC7 textures; SHA-256 {digest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    manifest = json.loads(Path(__file__).with_name("manifest.json").read_text(encoding="utf-8"))
    try:
        verify(args.archive, manifest)
    except (OSError, ValueError, KeyError, struct.error, RuntimeError,
            zipfile.BadZipFile, zstandard.ZstdError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
