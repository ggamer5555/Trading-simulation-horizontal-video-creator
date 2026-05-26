# Trading Chart Video Generator

This project contains a Python script, `generate videos.py`, that automatically creates short vertical trading-chart videos from MetaTrader 5 market data. It fetches random historical candle data, renders a dark themed chart with moving averages and a randomly selected technical indicator, generates voice-over audio from text prompts, adds animated captions and a glowing title overlay, then exports a finished MP4 video.

The script is designed for short-form social media content such as TikTok, Instagram Reels, and YouTube Shorts.

<img width="643" height="1036" alt="image" src="https://github.com/user-attachments/assets/846a6cc2-130e-4e71-9471-2027575c98eb" />


> Important: this script **does not place trades**. It only connects to MetaTrader 5 to download OHLCV candle data for chart/video generation.

---

## What the script does

At a high level, the script:

1. Chooses a random trading symbol from:
   - `EURUSD`
   - `BTCUSD`
   - `XAUUSD`

2. Chooses a random timeframe from:
   - `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`

3. Connects to MetaTrader 5 and downloads historical candles using `mt5.copy_rates_from_pos()`.

4. Randomly selects a chart indicator:
   - MACD
   - RSI
   - Aroon

5. Builds a vertical 1080x1920 style chart image using Matplotlib:
   - Candlestick chart
   - Moving average 13
   - Moving average 50
   - Indicator panel below the price chart
   - Random candle and line colors

6. Loads random text prompts from local `.txt` files.

7. Converts the prompts into voice audio using StreamElements TTS through `pyt2s`.

8. Generates a sequence of chart frames to simulate candles appearing over time.

9. Builds a video with MoviePy:
   - Static chart section
   - Animated chart section
   - Frozen final chart section
   - TTS voice-over
   - Timed glowing captions
   - Rainbow/glowing top overlay

10. Exports:
   - `intermediate_video.mp4`
   - `generated_videos/final_video_with_overlay.mp4`

11. Starts a scheduler that runs the video generation job immediately, then checks again every 8 hours.

---

## Main files and folders

Expected project layout:

```text
project-root/
├── generate videos.py
├── tts.txt
├── color1.txt
├── string1.txt
├── string2.txt
├── string3.txt
├── string4.txt
├── arialbd.ttf                  # optional but recommended
├── cookies2.txt                 # defined but not used in current script
├── sound_affects/
│   └── *.mp3                    # selected randomly but not currently mixed into final audio
├── output/
│   ├── static_*.png
│   ├── frame_*.png
│   └── tts*.mp3
└── generated_videos/
    └── final_video_with_overlay.mp4
```

The script creates `output/` and `generated_videos/` automatically if needed.

---

## Required input files

### `tts.txt`

Contains one voice name per line. The script randomly chooses one voice and sends it to StreamElements TTS.

Example:

```text
Brian
Amy
Joanna
Matthew
```

### `color1.txt`

Contains color names or hex values, one per line. The script randomly picks two distinct colors for chart lines.

Example:

```text
#00ffcc
#ff00ff
#ffff00
#00aaff
white
orange
```

### `string1.txt`, `string2.txt`, `string3.txt`, `string4.txt`

Each file contains possible caption/voice-over lines. The script randomly selects one line from each file.

Example `string1.txt`:

```text
Can this trading bot survive the next market move?
Watch this chart unfold in real time.
```

`string2.txt` can contain a number, and the script replaces standalone numbers with the randomly selected animation bar count.

Example `string2.txt`:

```text
The next 50 candles decide everything.
```

### `sound_affects/`

The script currently chooses a random MP3 sound effect from this folder, but the selected sound effect is not actually added to the final audio track in the current version.

---

## Dependencies

Install the main Python packages:

```bash
pip install pandas numpy matplotlib pillow pygame moviepy schedule MetaTrader5 pyt2s gTTS mplfinance
```

You also need:

- Python 3.9+
- FFmpeg available to MoviePy
- MetaTrader 5 installed and logged in
- A symbol list in MT5 that includes `EURUSD`, `BTCUSD`, and/or `XAUUSD`

On Windows, the `MetaTrader5` Python package normally expects the MT5 desktop terminal to be installed and accessible.

---

## How to run

From the project folder:

```bash
python "generate videos.py"
```

When started, the script:

1. Prints `✅ Scheduler started`
2. Runs one video-generation job immediately
3. Saves the final MP4 to:

```text
generated_videos/final_video_with_overlay.mp4
```

4. Keeps running and checks every 60 seconds for scheduled jobs
5. Runs the scheduled job every 8 hours

---

## Important scheduler behavior

The current scheduler only generates a video if this file does **not** already exist:

```text
generated_videos/final_video_with_overlay.mp4
```

That means the first run creates a video, but later scheduled runs reuse the existing file instead of generating a fresh one.

To force a new video, delete the existing file first:

```bash
rm generated_videos/final_video_with_overlay.mp4
```

On Windows PowerShell:

```powershell
Remove-Item generated_videos/final_video_with_overlay.mp4
```

---

## Output

Final output:

```text
generated_videos/final_video_with_overlay.mp4
```

Temporary/intermediate output:

```text
intermediate_video.mp4
output/static_*.png
output/frame_*.png
output/tts*.mp3
output/overlay_text.png
```

The final video contains:

- A vertical trading chart
- Random market symbol and timeframe
- Candlesticks with moving averages
- MACD, RSI, or Aroon indicator
- Generated TTS narration
- Timed captions
- Top overlay showing the symbol, timeframe, and link text

---

## Code walkthrough

### `generate_trading_video(output_path=...)`

The main video-generation function. It contains the full pipeline for choosing random settings, fetching MT5 candle data, generating charts, creating TTS audio, rendering animation frames, adding captions, and exporting the final MP4.

### `get_candles_from_mt5(symbol, count, mt5_timeframe)`

Initializes MetaTrader 5, downloads historical rates, converts the data into a Pandas DataFrame, formats the time column, and returns OHLCV data.

### `calculate_indicator_data(df)`

Adds indicator columns to the DataFrame depending on the randomly selected indicator:

- MACD: `ema12`, `ema26`, `MACD`, `signal`, `macd_diff`
- RSI: `RSI`
- Aroon: `aroon_up`, `aroon_down`

### `save_chart(df, filename, buffer=50)`

Creates a chart image with:

- Candlesticks
- MA 13
- MA 50
- Indicator subplot
- Dark background
- Randomized colors

This function saves each rendered chart frame as a PNG.

### `generate_tts(text, filename)`

Uses StreamElements TTS through `pyt2s` to generate MP3 narration for each selected text line.

If the selected voice fails, it falls back to the default StreamElements voice.

### `get_rainbow_overlay_clip(text, duration, video_size)`

Creates an animated rainbow/glowing overlay using Pygame and MoviePy. This is placed near the top of the video and displays the chosen symbol/timeframe plus link text.

### `make_timed_caption_clip(...)`

Creates animated glowing captions that are timed to match each TTS audio section.

### `create_video_if_not_exists()`

Checks whether the final video already exists. If it does not exist, it calls `generate_trading_video()`.

### `job()`

Runs garbage collection and then calls the main generation process.

### Scheduler block

At the bottom of the script, the scheduler:

```python
job()
schedule.every(8).hours.do(job)
```

This runs the job once immediately, then schedules future jobs every 8 hours.

---

## Configurable values

You can edit these values in the script.

### Output path

```python
VIDEO_DIR = Path("generated_videos")
VIDEO_FILENAME = "final_video_with_overlay.mp4"
```

### Description text

```python
DESCRIPTION = "trading game! #tradingforex #forexstrategy #cryptotrading #tradingcrypto #bitcoin #forextrading #stocks"
```

This variable is currently defined but not used for uploading inside this script.

### Symbols

```python
pairs = ['EURUSD', 'BTCUSD', 'XAUUSD']
```

### Timeframes

```python
timeframes = {
    '1m': mt5.TIMEFRAME_M1,
    '5m': mt5.TIMEFRAME_M5,
    '15m': mt5.TIMEFRAME_M15,
    '30m': mt5.TIMEFRAME_M30,
    '1h': mt5.TIMEFRAME_H1,
    '4h': mt5.TIMEFRAME_H4,
    '1d': mt5.TIMEFRAME_D1,
}
```

### Indicators

```python
selected_indicator = random.choice(["MACD", "RSI", "AROON"])
```

### Schedule interval

```python
schedule.every(8).hours.do(job)
```

---

## Notes and current limitations

- The script imports some packages that are not used in the current version, such as `gTTS`, `mplfinance`, and some MoviePy audio/video classes.
- `sound_affects/` MP3 files are selected randomly, but the chosen sound effect is not mixed into the final audio.
- The final video is not regenerated every 8 hours unless the existing MP4 is deleted first.
- `cookies2.txt`, `DESCRIPTION`, and commented upload-related names suggest planned TikTok/YouTube/Instagram upload functionality, but this script does not currently upload anything.
- `matplotlib.use("Agg")` makes the script suitable for non-GUI rendering.
- `change_settings({"IMAGEMAGICK_BINARY": ""})` disables ImageMagick usage for MoviePy text rendering.
- The script can use significant CPU, memory, and disk space because it renders many PNG chart frames and then encodes video.
- MetaTrader 5 data access can fail if MT5 is not installed, not logged in, the symbol is unavailable, or the terminal is not connected.

---

## Troubleshooting

### `MT5 initialize() failed`

Make sure:

- MetaTrader 5 is installed
- You are logged into an account
- The terminal has an active connection
- The selected symbol exists in Market Watch

### `No data returned from MT5`

Try:

- Opening the symbol in MT5
- Loading more history in the terminal
- Removing unavailable symbols from `pairs`
- Testing a different timeframe

### MoviePy/FFmpeg export errors

Install FFmpeg and make sure it is available on your system PATH.


