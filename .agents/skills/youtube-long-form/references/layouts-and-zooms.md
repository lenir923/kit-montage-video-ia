# Layouts, switching and zooms (long-form tutorial, 16:9 output)

The target feel is Nate Herk's recent edits: calm, clean, premium. The frame always
has ONE focus. Movement is constant but small. Transitions are motion, not cuts,
whenever the layout changes. Nothing decorative: every card, zoom or switch serves
the sentence being said.

## Sources to expect

- Face cam from an iPhone, often PORTRAIT (1080x1920 after prep). Never crop it
  to a tight 16:9 face shot (1080x608 upscaled: soft, and too tight on the head).
  The face is shown as a card: see `CAM_CARD`.
- Screen recording from a Retina Mac (2940x1912, ratio 1.54, not 16:9). Native
  width allows about 1.5x zoom with no upscaling, 2x stays readable.

## The layouts

| Id | What the viewer sees | Default use |
|---|---|---|
| `CAM_CARD` | The portrait source cropped top and bottom to a square or a slightly tall rectangle (1:1 to 4:5, head and shoulders with air above the head, NOT a tight face crop), enlarged, centred (or shifted aside when a beat card needs room), rounded corners and soft shadow. Behind it: the DA background, or the screen recording of that moment heavily blurred and darkened. | All [CAM] parts: hook, promise, transitions, warnings, CTA. Emphasis = a moderate push of the card (max ~110 %), never a tight face crop |
| `SCREEN_PIP` | Screen as a rounded card filling most of the frame on the background (margins ~40 px, the 1.54 ratio fits with bars used by the background), face in a small portrait rounded PiP bottom-right (~300x450). | All [ÉCRAN] parts while the speaker acts on screen |
| `SCREEN_FOCUS` | Same, zoomed on the area that matters; PiP stays unless it covers the target (then it slides out). | Reading a result, typing a prompt, a number read aloud |
| `SCREEN_SOLO` | Screen alone, no PiP, speed badge ("x6") when sped up. | Timelapses, waiting for Claude, tables appearing |

The same video element moves between layouts: the face card flies and shrinks into
the PiP, the screen card grows from the side. Use FLIP-style transforms on a
non-timed wrapper (0.5-0.7 s, `power3.inOut` or `expo.inOut`), never a hard cut or a
cross-dissolve between layouts. A plain cut is fine WITHIN a layout (jump cut).

## Switching rules

1. The script's markers give the default per section: [CAM] = cam layouts only,
   [ÉCRAN] = screen layouts.
2. Inside an [ÉCRAN] section, go to `CAM_CARD` when
   the speaker explains without acting: the screen is static (`analysis/activity.json`
   act near 0 over the span) AND the sentence is a conclusion, an opinion or a
   lesson ("Personne dans la boîte ne l'avait vu.", "Ça, c'est un coup de fil à
   passer demain matin."). Come back to the screen as soon as the speaker acts again.
3. Minimum 3 s per layout. No more than one layout change every ~6 s on average.
4. Show a screen range only when it serves what is said (the teleprompter or the
   Claude Code panel are not secret, just useless on screen). Never show a black
   screen frame (before the recording started). If the words need a visual there,
   use `CAM_CARD` + a card that shows the content cleanly.
5. The screen card may be cropped to what matters (the chat, the sheet, the pane)
   rather than the whole desktop: it reads better. Blur or crop anything private
   (chat history, browser tabs, names, emails, phone numbers) before it goes on air.
6. Prompts typed on screen: show the typing sped up if long, then zoom so the full prompt
   is readable for at least 2 s, or overlay it as a clean text card.

## Zooms

Two layers, never fighting each other:

- **Continuous drift** (the base life of the frame): very slow scale drift on the
  active video wrapper, alternating in and out, about 2 %/s, max 107 %. It gives the
  frame a "permanent movement"; keep it subtle on screen shots.
- **Intentional moves** (the meaning):
  - Face (the card, never a tight crop): punch-in 1.00 -> 1.08 on a stressed word (a number, "choque", "personne",
    "gratuit"), hard or 0.15 s ease, at most one per 8-10 s; or a slow push over a
    whole key sentence. At every jump cut inside a continuous face shot, alternate
    the framing (1.00 <-> 1.08 + slight reframe) so the jump reads as intentional.
  - Screen: zoom to the region of action. Target = the bbox from
    `analysis/activity.json` around that time (converted from screen time with the
    sync offset), or the known UI area (prompt box while typing, the answer while
    reading, the Excel pane, the chart that appears). Ease in 0.6-0.8 s
    `power2.inOut`, hold while it matters, ease out. 1.3x to 1.8x. Never zoom during
    fast scrolling, never zoom so the cursor or the key number leaves the frame.
  - Numbers read aloud on screen ("55 réclamations sur 148", "moins 43 pour cent"):
    zoom + a highlight shape drawn around the cell or line + optional counter card.

## Motion graphics beats

Follow `video-storytelling` (one arc, callbacks) and `hyperframes-video-beats`
(anchors on exact transcript words, entry 0.2 s after to 1.8 s before the word).
One idea per beat, one beat at a time, the face or the screen stays the hero.
Good beats for a tutorial: the plan of the video as a persistent 3-step tracker that
comes back at each transition (callback), big numbers with counters, a message
bubble for a quoted person, a drawn file tree, a before/after table, a list of
warnings, the CTA card with the lead magnet.

## Subtitles

Long-form YouTube: optional and discreet (many viewers use YouTube's own
captions). If used: 2 lines max, bottom, clean sans, no word-by-word karaoke, hidden
while a card sits in the same area. Decide once for the whole video and stick to it.

## Sound

Voice dominates, always. Music bed very low under speech (about -28 to -30 LUFS
relative feel, ducked), louder during timelapses and transitions. Soft whoosh on
layout transitions, subtle pop on card entries, never on every cut.
