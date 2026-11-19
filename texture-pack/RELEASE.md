# Silicon Valley 4x AI Textures 1.0.0

Optional texture-only pack for the unchanged upstream Space Station Silicon Valley recompilation.
No ROM, executable, gameplay patches, or model weights are included.

## Install

1. Use the upstream game with your own supported US 1.0 ROM.
2. Download `SSSV_4x_AI_Textures.rtz` below (approximately 157 MiB).
3. Close the game and copy the `.rtz`, without extracting it, into its `mods` directory.
4. Enable **Silicon Valley 4x AI Textures** in the launcher's **Mods** menu.

For portable installations, `mods` is beside the game executable. See the repository
README for non-portable paths, screenshots, processing credits, and coverage limitations.
Disable the pack in Mods to restore native textures. Do not enable conflicting texture packs.

## Contents and verification

- 35,601 RT64 v5 replacement mappings and 35,433 BC7 DDS textures with full mip chains.
- 4x AI-upscaled terrain, artwork, fonts, HUD, and effects where verified bindings exist.
- RT64 streaming and low-mip cache. No unrelated rendering or gameplay modifications.
- Native-versus-upscaled gameplay screenshots in the repository README.
- Windows portable v0.2.0 tested locally; other platforms are not runtime-tested here.
- Generated textures, framebuffers, and unseen palette variants may still render natively.

SHA-256 of `SSSV_4x_AI_Textures.rtz`:

```text
39b87c7a358cb2068af26a980f06491a1a03f924731c0676126439f1c1cba3a0
```

`SHA256SUMS.txt` and `manifest.json` are attached. The repository's Python verifier checks
the digest, every archive entry's CRC, all mappings, and BC7 DDS mip-chain payloads.
Download the `.rtz` asset, not GitHub's automatically generated source-code ZIP.

## Credits and rights

UniScale Balanced/Restore: kim2091 (model license CC-BY-NC-SA-4.0).
DitherDeleterV3 Smooth: mutin-choler (WTFPL). SGI: chrisnonyminus (GPL-3.0-only).
No model weights are distributed. Model licenses are not a blanket license for game artwork.
Original game artwork remains the property of its respective rights holders; this is an
unofficial fan project, not an official release or endorsement. Do not assume commercial rights.
Thanks to the upstream recompilation, decompilation, N64Recomp, and RT64 contributors.
