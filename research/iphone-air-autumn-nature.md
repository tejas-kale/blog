# Research notes: autumn nature photography on iPhone Air

Gathered 2026-09-06 for a month-long neighbourhood project in Berlin. The tutorial in `content/drafts/iphone-air-autumn-photography.md` is written against these constraints. Do not copy Pro-model advice (ultra-wide, telephoto, macro, ProRAW) onto this phone.

## Hardware (iPhone Air)

Primary sources: [Apple iPhone Air specs](https://www.apple.com/iphone-air/specs/), [Apple newsroom](https://www.apple.com/newsroom/2025/09/introducing-iphone-air-a-powerful-new-iphone-with-a-breakthrough-design/), [Trusted Reviews](https://www.trustedreviews.com/reviews/apple-iphone-air), [AppleInsider Camera app guide](https://appleinsider.com/articles/26/01/14/how-to-master-the-camera-app-on-iphone-air).

Rear camera is a **single 48MP Fusion Main**:

| Spec | Value |
| --- | --- |
| Focal length | 26 mm equivalent, ƒ/1.6 |
| Stabilisation | Sensor-shift OIS |
| Default capture | 24MP HEIF (fusion of 48MP detail + binned frames) |
| Optional | 48MP HEIF/JPEG in Photo mode |
| 2× | 12MP optical-quality crop, 52 mm, ƒ/1.6, same sensor-shift OIS |
| Digital zoom | Up to 10× (avoid for stills you intend to publish) |
| Extra framings | Customisable default lens: 28 mm and 35 mm crops of the main camera |
| Formats | HEIF and JPEG only — **no Apple ProRAW** |
| Missing vs Pro | Ultra-wide, dedicated telephoto, macro mode, spatial photos, Apple Log |

Computational stack that *is* present: Photonic Engine, Deep Fusion, Smart HDR 5, Night mode, latest-generation Photographic Styles (including Bright), next-generation portraits with Focus/Depth Control, panorama up to 63MP.

Front camera is 18MP Center Stage (square sensor). Useful for Dual Capture video and selfies; not the tool for this nature series.

Physical controls: Action button (can open Camera) and **Camera Control** on the lower-right edge (launch, shutter, half-press for Exposure / Zoom / Styles / Tone / Depth).

## What 48MP vs 24MP actually means

Apple’s default 24MP Fusion file is the better everyday choice: it keeps Smart HDR, Deep Fusion, and **depth data** so a Photo-mode shot can become a portrait later in Photos.

48MP HEIF (enable Settings → Camera → Formats → Resolution Control, then tap HEIF 24 in the Camera UI) keeps more texture for landscapes you might crop. Trade-offs reported across Apple’s pipeline and independent write-ups:

- Photo mode only. Night mode, flash, Live Photos, 2×, and Portrait typically fall back to 12MP or 24MP without depth-for-later.
- Files are larger; GitHub Pages should never receive the full 48MP original.

Practical rule used in the tutorial: **24MP HEIF by default; 48MP only for a still landscape you will crop or print; export a JPEG ≤ 2500 px on the long edge for the blog.**

## Photographic Styles (iOS 26)

Apple Support: [Use Photographic Styles](https://support.apple.com/en-gb/guide/iphone/iph629d2cd37/ios), [Edit photos](https://support.apple.com/guide/iphone/edit-photos-and-videos-iphb08064d57/26/ios/26).

On latest-generation Styles (iPhone 16 and later, including Air):

- The style is part of the capture pipeline, visible in the viewfinder, and can be changed later **if** capture format is High Efficiency (HEIF).
- Bright “brightens skin tones and applies a pop of vibrance” — useful for people, usually too punchy for foliage.
- For autumn, Standard or a slightly warm style, then small Tone/Color/Intensity edits in Photos, is enough. Styles are not Instagram filters; they retune regions of the image rather than a global LUT.

## Camera technique (stock app)

Apple Support: [Set up your shot](https://support.apple.com/guide/iphone/set-up-your-shot-iph3dc593597/26/ios/26).

- Grid and Level: Settings → Camera.
- Tap to focus/expose; drag the sun for exposure; touch-and-hold for **AE/AF Lock**.
- Exposure compensation in the Camera Control overlay or the settings drawer also locks until Camera is closed unless Preserve Settings → Exposure Adjustment is on.
- Volume buttons fire the shutter; volume-up hold = burst.
- Panorama: rotate from the hips, not the arms; this is the Air’s substitute for an ultra-wide landscape.

Close-ups: there is **no macro mode**. Move in until autofocus hunts, then step back a few centimetres. 2× (52 mm) often looks better for a leaf or mushroom than filling the 26 mm frame from too close.

## Light editing (Photos app only)

Allowed in this project: straighten/perspective, modest crop, exposure/highlights/shadows, warmth, Photographic Style intensity, a touch of vibrance, optional definition. Not allowed: heavy Lightroom colour-mixer “fake autumn”, sky replacement, or Apple Intelligence Clean Up as a creative tool.

Reason: HEIF from Smart HDR 5 is already a finished file. Aggressive edits posterise skies and make yellows neon. Overcast autumn light already saturates foliage; the job is mostly not to blow the bright leaves.

## Berlin autumn, neighbourhood scale

Peak colour in Berlin is typically **mid to late October**, with usable colour from late September into early November depending on frost. Days shorten quickly; by late October sunset is mid-afternoon.

Neighbourhood subjects that do not require a “destination” shoot:

- Street trees (linden, maple, oak, plane) against façades and Hinterhöfe
- Leaf litter, puddles, tram tracks, canal towpaths (e.g. Landwehrkanal if that is local)
- A single Kiez park rather than Tiergarten/Grunewald as the default
- Weather: high overcast (even colour), fog, rain on glass, low sun through thinning canopy

Destination parks (Tiergarten, Treptower, Grunewald, Botanischer Garten) are optional weekend extras, not the syllabus. The pedagogical point is repeating the same two or three nearby blocks so light and colour changes are visible week to week.

## Sources not followed

Moment / generic “iPhone landscape” guides that assume ProRAW, ND/CPL clip-on glass, ultra-wide, and third-party manual apps. Halide or Moment Pro Camera 2 can drive the Air’s Camera Control, but this project stays on the stock Camera + Photos apps so the series is reproducible without extra software.
