import gc
def generate_trading_video(output_path="generated_videos/final_video_with_overlay.mp4"):
    import gc
    from pyt2s.services import stream_elements
    import os
    import random
    import pandas as pd
    import mplfinance as mpf
    from gtts import gTTS
    from moviepy.editor import (
        ImageClip, AudioFileClip, concatenate_videoclips,
        CompositeAudioClip, CompositeVideoClip
    )
    import MetaTrader5 as mt5
    from moviepy.config import change_settings
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib.pyplot as plt
    from moviepy.audio.AudioClip import AudioArrayClip, concatenate_audioclips
    import numpy as np

    from moviepy.editor import (
        ImageClip, AudioFileClip, concatenate_videoclips,
        CompositeAudioClip, CompositeVideoClip, VideoFileClip
    )

    import matplotlib.dates as mdates
    import matplotlib.patches as mpatches

    import pygame
    from moviepy.editor import VideoClip

    from moviepy.video.VideoClip import VideoClip
    import pygame
    import numpy as np
    import math
    import re

    import matplotlib
    matplotlib.use("Agg")

    candle_color_presets = [
        ("#26a69a", "#ef5350"),  # teal / red
        ("#2ecc71", "#e74c3c"),  # green / red
        ("#8bc34a", "#f44336"),  # lime green / red
        ("#00bcd4", "#ff9800"),  # cyan / orange
        ("#ffffff", "#ff00ff"),  # white / magenta
        ("#90caf9", "#f48fb1"),  # light blue / pink
    ]

    # Randomly choose a preset
    up_color, down_color = random.choice(candle_color_presets)




    # Smooth linear interpolation between two colors
    def lerp(color1, color2, t):
        return tuple(int(float(c1) + (float(c2) - float(c1)) * t) for c1, c2 in zip(color1, color2))


    # Smooth color transition using sine function
    def smooth_transition(t, color1, color2):
        phase = (math.sin(t * math.pi / 3) + 1) / 2
        return lerp(color1, color2, phase)


    # Glowing effect with slower pulsing white shadow
    def glowing_effect(t):
        intensity = int(180 + 75 * math.sin(t * math.pi))  # Slower pulse, between 180 and 255
        return (intensity, intensity, intensity)


    # Generate rainbow overlay clip with smooth color transitions and glowing effect
    def get_rainbow_overlay_clip(text, duration, video_size):
        # Define color pairs
        color_sets = [
            ((255, 165, 0), (255, 0, 0)),       # Orange to Red
            ((173, 216, 230), (144, 238, 144)), # Light Blue to Light Green
            ((255, 105, 180), (255, 0, 0)),     # Pink to Red
            ((0, 255, 0), (255, 255, 0))        # Green to Yellow
        ]
        color1, color2 = random.choice(color_sets)

        width, height = video_size
        pygame.init()
        font = pygame.font.SysFont("Arial", 65)

        def make_frame(t):
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            lines = text.split("\n")
            y = 10

            for line_idx, line in enumerate(lines):
                total_width = sum(font.size(char)[0] for char in line)
                x = (width - total_width) // 2
                for char_idx, char in enumerate(line):
                    color = smooth_transition(t + char_idx * 0.1, color1, color2)
                    glow_color = glowing_effect(t)

                    # Draw pulsing glowing effect
                    glow_surface = font.render(char, True, glow_color)
                    for offset in range(-2, 3):
                        surface.blit(glow_surface, (x + offset, y + offset))

                    # Draw main text
                    char_surface = font.render(char, True, color)
                    surface.blit(char_surface, (x, y))
                    x += char_surface.get_width()
                y += font.get_linesize()

            rgb = pygame.surfarray.pixels3d(surface).transpose(1, 0, 2).copy()
            alpha = pygame.surfarray.pixels_alpha(surface).transpose(1, 0).copy() / 255.0
            return rgb, alpha

        def make_rgb(t):
            rgb, _ = make_frame(t)
            return rgb

        def make_mask(t):
            _, alpha = make_frame(t)
            return alpha

        return VideoClip(make_rgb, duration=duration).set_mask(
        VideoClip(make_mask, ismask=True, duration=duration)
        ).set_position(("center", 0))




    aroon_val = [14, 20, 30]
    aroon_length = random.choice(aroon_val)

    rsi_val = [14, 20, 30]
    rsi_length = random.choice(rsi_val)

    bars2 = [150, 200, 250, 300]
    bars = [50, 100, 25]
    #chosen_bars = random.choice(bars)

    BUFFER = 50
    VISIBLE_START_bars = random.choice(bars2)
    VISIBLE_START = VISIBLE_START_bars #+ BUFFER
    total_duration = 2.5  # in seconds
    ANIMATION_BARS = random.choice(bars)
    ANIM_END = VISIBLE_START + ANIMATION_BARS #+ BUFFER

    CANDLES_NEEDED = VISIBLE_START + BUFFER + ANIM_END  # ~350



    OUTPUT_DIR = "output"
    SFX_DIR = "sound_affects"
    #ANIM_START = 151
    #VISIBLE_START = 100
    #ANIM_END = 200
    FRAME_DURATION = (total_duration / ANIMATION_BARS) * 5



    ma_short = 13
    ma_long = 50

    change_settings({"IMAGEMAGICK_BINARY": ""})  # Disable ImageMagick
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open("tts.txt", "r") as f:
        voices = [line.strip() for line in f if line.strip()]
    selected_voice = random.choice(voices)

    pairs = ['EURUSD', 'BTCUSD', 'XAUUSD']
    # Updated Timeframes
    timeframes = {
        '1m': mt5.TIMEFRAME_M1,
        '5m': mt5.TIMEFRAME_M5,
        '15m': mt5.TIMEFRAME_M15,
        '30m': mt5.TIMEFRAME_M30,
        '1h': mt5.TIMEFRAME_H1,
        '4h': mt5.TIMEFRAME_H4,
        '1d': mt5.TIMEFRAME_D1,
    }

    def load_two_distinct_colors(path='color1.txt'):
        with open(path, 'r') as f:
            colors = [line.strip() for line in f if line.strip()]
        if len(colors) < 2:
            raise ValueError("Need at least 2 distinct colors in color1.txt")
        color1 = random.choice(colors)
        colors.remove(color1)
        color2 = random.choice(colors)
        return color1, color2


    selected_indicator = random.choice(["MACD", "RSI", "AROON"])
    color_ma20, color_ma50 = load_two_distinct_colors()
    color1, color2 = load_two_distinct_colors()
    print(selected_indicator, color_ma20 , color_ma50, color2, color1)

    def calculate_indicator_data(df: pd.DataFrame):
        """Calculate and return indicator-specific columns in-place."""
        if selected_indicator == "MACD":
            df['ema12'] = df['close'].ewm(span=12).mean()
            df['ema26'] = df['close'].ewm(span=26).mean()
            df['MACD'] = df['ema12'] - df['ema26']
            df['signal'] = df['MACD'].ewm(span=9).mean()
            df['macd_diff'] = df['MACD'] - df['signal']
        elif selected_indicator == "RSI":
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(rsi_length).mean()
            loss = -delta.where(delta < 0, 0).rolling(rsi_length).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
        elif selected_indicator == "AROON":
            period = aroon_length
            df['aroon_up'] = df['high'].rolling(period).apply(lambda x: 100 * (period - x[::-1].argmax()) / period, raw=True)
            df['aroon_down'] = df['low'].rolling(period).apply(lambda x: 100 * (period - x[::-1].argmin()) / period, raw=True)


    def get_candles_from_mt5(symbol: str, count: int, mt5_timeframe) -> pd.DataFrame:
        if not mt5.initialize():
            raise RuntimeError(f"MT5 initialize() failed: {mt5.last_error()}")

        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
        mt5.shutdown()

        if rates is None or len(rates) == 0:
            raise ValueError("No data returned from MT5")

        df = pd.DataFrame(rates)

        # Drop rows with NaN or None values in any column
        df = df.dropna()

        if df.empty:
            raise ValueError("All returned data was NaN or invalid")

        if df.empty:
            raise ValueError("All candles had invalid or zero OHLC values")

        # Convert time from Unix timestamp to datetime
        df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)

        # Set 'time' as the index for the dataframe
        df.set_index('time', inplace=True)

        # Rename the columns
        df.rename(columns={
            'open': 'open', 'high': 'high', 'low': 'low', 
            'close': 'close', 'tick_volume': 'volume'
        }, inplace=True)
        return df[['open', 'high', 'low', 'close', 'volume']]



    def save_chart(df: pd.DataFrame, filename: str, buffer: int = 50):
        #df = df.copy()

            # Downcast numeric columns
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col], downcast='float')

        # Calculate indicators on the full dataset
        df[f'MA{ma_short}'] = df['close'].rolling(ma_short).mean()
        df[f'MA{ma_long}'] = df['close'].rolling(ma_long).mean()
        calculate_indicator_data(df)

        # Assign synthetic time index
        #df['time'] = range(len(df))
        df['time'] = np.arange(len(df))  # Faster than range() + pandas

        # Slice for plotting (apply buffer)
        df_plot = df.iloc[buffer:].reset_index(drop=True)

        times = df_plot['time'].values
        spacing = np.median(np.diff(times)) if len(times) > 1 else 1
        candle_width = spacing * 0.95

        plt.style.use("dark_background")
        dpi = 100
        fig, (ax1, ax2) = plt.subplots(
            2, 1,
            figsize=(10.8, 19.2),
            sharex=True,
            gridspec_kw={'height_ratios': [6, 3]}
        )

        # # Plot candles
        # for _, row in df_plot.iterrows():
        #     color = up_color if row['close'] >= row['open'] else down_color
        #     ax1.plot([row['time'], row['time']], [row['low'], row['high']], color=color, linewidth=0.8)
        #     rect = mpatches.Rectangle(
        #         (row['time'] - candle_width / 2, min(row['open'], row['close'])),
        #         candle_width,
        #         abs(row['close'] - row['open']),
        #         color=color
        #     )
        #     ax1.add_patch(rect)
        rows = df_plot[['time', 'open', 'high', 'low', 'close']].values
        for row in rows:
            time, open_, high, low, close = row
            color = up_color if close >= open_ else down_color
            ax1.plot([time, time], [low, high], color=color, linewidth=0.8)
            rect = mpatches.Rectangle(
                (time - candle_width / 2, min(open_, close)),
                candle_width,
                abs(close - open_),
                color=color
            )
            ax1.add_patch(rect)


        # Plot moving averages
        ax1.plot(times, df_plot[f'MA{ma_short}'], label=f'MA {ma_short}', color=color_ma20)
        ax1.plot(times, df_plot[f'MA{ma_long}'], label=f'MA {ma_long}', color=color_ma50)
        ax1.set_ylabel("Price", fontsize=20, weight='bold', color='white')
        ax1.legend(loc="upper left", fontsize=20)
        ax1.tick_params(axis='y', labelsize=15)
        ax1.grid(True, alpha=0.2)

        # Plot selected indicator
        if selected_indicator == "MACD":
            ax2.plot(times, df_plot["MACD"], label="MACD", color=color1)
            ax2.plot(times, df_plot["signal"], label="Signal", color=color2)
            ax2.set_ylabel("MACD", fontsize=20, weight='bold', color='white')
        elif selected_indicator == "RSI":
            ax2.plot(times, df_plot["RSI"], color=color1, label=f'RSI {rsi_length}')
            ax2.axhline(70, color='red', linestyle='--', linewidth=1)
            ax2.axhline(30, color='green', linestyle='--', linewidth=1)
            ax2.set_ylabel("RSI", fontsize=20, weight='bold', color='white')
        elif selected_indicator == "AROON":
            ax2.plot(times, df_plot["aroon_up"], color='green', label=f'Aroon Up {rsi_length}')
            ax2.plot(times, df_plot["aroon_down"], color='red', label=f'Aroon Down {rsi_length}')
            ax2.set_ylabel("Aroon", fontsize=20, weight='bold', color='white')

        ax2.tick_params(axis='y', labelsize=15)
        ax2.legend(loc="upper left", fontsize=15)
        ax2.grid(True, alpha=0.2)

        fig.tight_layout()
        plt.savefig(filename, dpi=dpi, facecolor='black')
        plt.close(fig)
        plt




    def generate_tts(text: str, filename: str, voice_list_path: str = "tts.txt"):
        try:
            data = stream_elements.requestTTS(text, selected_voice)
        except Exception as e:
            print(f"❌ Failed to generate TTS with {selected_voice}, using default voice. Error: {e}")
            data = stream_elements.requestTTS(text)

        with open(filename, "wb") as f:
            f.write(data)
        print(f"✅ TTS saved: {filename} (voice: {selected_voice})")


    def load_random_line(filepath: str) -> str:
        with open(filepath, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        return random.choice(lines)

    def create_text_image(text: str, width: int = 720, height: int = 100, initial_font_size: int = 36) -> str:
        lines = text.splitlines()
        font_path = "arialbd.ttf"  # bold font fallback

        font_size = initial_font_size
        while font_size > 10:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()

            too_wide = any(font.getbbox(line)[2] > width - 20 for line in lines)
            if not too_wide:
                break
            font_size -= 1

        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        total_height = sum(font.getbbox(line)[3] - font.getbbox(line)[1] + 5 for line in lines)
        y = (height - total_height) // 2

        for line in lines:
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            draw.text((x, y), line, font=font, fill="white")
            y += text_height + 5

        output_path = os.path.join(OUTPUT_DIR, "overlay_text.png")
        img.save(output_path)
        return output_path


    def select_stable_data(df: pd.DataFrame, total_needed: int, visible_start: int, max_attempts: int = 100) -> pd.DataFrame:
        for _ in range(max_attempts):
            start_idx = random.randint(50, len(df) - total_needed - 1)
            candidate = df.iloc[start_idx:start_idx + total_needed].copy()

            filtered = candidate.loc[(candidate['open'] != candidate['close']) | (candidate['high'] != candidate['low'])]

            if len(filtered) >= visible_start + 1:
                return candidate  # return the full candidate (not filtered), so MAs and indicators work

        raise ValueError("❌ Could not find a usable slice with enough non-flat candles.")

    # --- FETCH DATA ---
    symbol = random.choice(pairs)
    tf_key = random.choice(list(timeframes))
    mt5_tf = timeframes[tf_key]
    print(f"Selected: {symbol} [{tf_key}] | Indicator: {selected_indicator}")

    df = get_candles_from_mt5(symbol, 10000, mt5_tf)

    if len(df) < CANDLES_NEEDED + 1:
        raise ValueError("Not enough data")

    data = select_stable_data(df, total_needed=CANDLES_NEEDED, visible_start=VISIBLE_START)
    print(len(data))
    data = data.astype({
        'open': 'float32',
        'high': 'float32',
        'low': 'float32',
        'close': 'float32'
    })

    # --- STATIC IMAGE ---
    #STATIC_END = ANIM_END

    static_img = os.path.join(OUTPUT_DIR, f"static_{VISIBLE_START}.png")
    save_chart(data.iloc[:VISIBLE_START + 1], static_img, buffer=50)
    gc.collect()










    # --- TTS TEXTS & SFX ---
    string1 = load_random_line('string1.txt')
    string2 = load_random_line('string2.txt')
    string2 = re.sub(r"\b\d+\b", str(ANIMATION_BARS), string2)

    string3 = load_random_line('string3.txt')
    string4 = load_random_line('string4.txt')

    tts_paths = []
    for idx, txt in enumerate([string1, string2, string3, string4], 1):
        path = os.path.join(OUTPUT_DIR, f"tts{idx}.mp3")
        generate_tts(txt, path)
        tts_paths.append(path)

    sfx_files = [f for f in os.listdir(SFX_DIR) if f.endswith(".mp3")]
    sfx_path = os.path.join(SFX_DIR, random.choice(sfx_files))

    # --- ANIMATION FRAMES ---
    frame_paths = []

    # for i in range(VISIBLE_START + 2 , ANIM_END + 1):
    #     img_path = os.path.join(OUTPUT_DIR, f"frame_{i}.png")
    #     save_chart(data.iloc[:i], img_path, buffer=50)
    #     frame_paths.append(img_path)

    def is_similar(row1, row2, threshold=0.0001):  # 0.01% = 0.0001
        # Only compare OHLC or relevant numerical columns
        cols = ['open', 'high', 'low', 'close']
        
        a = row1[cols].values.astype(np.float32)
        b = row2[cols].values.astype(np.float32)
        
        # Avoid divide-by-zero by adding small epsilon
        relative_diff = np.abs(a - b) / (np.abs(a) + 1e-8)
        
        return np.all(relative_diff < threshold)

    previous_row = None

    for i in range(VISIBLE_START + 2, ANIM_END + 1, 5):  # 🔁 Step every 2 bars
        current_row = data.iloc[i]

        if previous_row is not None and is_similar(previous_row, current_row):
            frame_paths.append(frame_paths[-1])  # Reuse last image
            continue

        img_path = os.path.join(OUTPUT_DIR, f"frame_{i}.png")
        save_chart(data.iloc[:i], img_path, buffer=50)
        frame_paths.append(img_path)
        gc.collect()

        previous_row = current_row



    # --- FUNCTION TO GENERATE SILENCE ---
    def generate_silence(duration=0.25, fps=15):
        samples = np.zeros(int(duration * fps))
        return AudioArrayClip(samples.reshape(-1, 1), fps=fps)



    from moviepy.editor import (
        concatenate_audioclips, AudioFileClip, VideoFileClip,
        CompositeVideoClip, concatenate_videoclips, ImageClip
    )
    from moviepy.video.VideoClip import VideoClip
    import pygame
    import textwrap

    # Fix: Prevent TTS4 replay by precisely aligning clips
    def smooth_audio(audio_clip, fade_duration=0.25):
        return audio_clip.audio_fadeout(fade_duration)


    pygame.font.init()
    #caption_font = pygame.font.SysFont("Arial", 40, bold=True)

    import textwrap

    def make_timed_caption_clip(text, start, duration, video_size, font_size=70, max_chars_per_line=20):
        width, height = video_size
        pygame.init()
        font = pygame.font.SysFont("Arial", font_size)

        # Wrap text to multiple lines
        wrapped_lines = textwrap.wrap(text, width=max_chars_per_line)
        line_height = font.get_linesize()

        def make_frame(t_local):
            t_global = t_local + start
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            y = height - 140 - len(wrapped_lines) * line_height

            for line in wrapped_lines:
                total_width = sum(font.size(char)[0] for char in line)
                x = (width - total_width) // 2
                for char_idx, char in enumerate(line):
                    color = smooth_transition(t_global + char_idx * 0.1, (255, 255, 255), (255, 255, 255))
                    glow_color = glowing_effect(t_global)

                    # glow effect
                    glow_surface = font.render(char, True, glow_color)
                    for offset in range(-2, 3):
                        surface.blit(glow_surface, (x + offset, y + offset))

                    # main character render
                    char_surface = font.render(char, True, color)
                    surface.blit(char_surface, (x, y))
                    x += char_surface.get_width()
                y += line_height

            rgb = pygame.surfarray.pixels3d(surface).transpose(1, 0, 2).copy()
            alpha = pygame.surfarray.pixels_alpha(surface).transpose(1, 0).copy() / 255.0
            return rgb, alpha

        def make_rgb(t): return make_frame(t)[0]
        def make_mask(t): return make_frame(t)[1]

        return VideoClip(make_rgb, duration=duration).set_mask(
            VideoClip(make_mask, ismask=True, duration=duration)
        ).set_start(start).set_position(("center", -500))



    # --- LOAD AUDIO CLIPS (NO SFX) ---------------------------------------------
    clip1_audio = AudioFileClip(tts_paths[0])
    clip2_audio = AudioFileClip(tts_paths[1])
    tts3_audio = AudioFileClip(tts_paths[2])
    tts4_audio = AudioFileClip(tts_paths[3])

    # Add silence before and after last TTS
    tts4_audio = concatenate_audioclips([
        generate_silence(0.3),
        tts4_audio,
        generate_silence(0.5)
    ])

    # Freeze durations (MoviePy stability)
    clip1_audio = clip1_audio.set_duration(clip1_audio.duration)
    clip2_audio = clip2_audio.set_duration(clip2_audio.duration)
    tts3_audio = tts3_audio.set_duration(tts3_audio.duration)
    tts4_audio = tts4_audio.set_duration(tts4_audio.duration)

    # --- BUILD FINAL AUDIO TRACK -----------------------------------------------
    full_audio = concatenate_audioclips([
        clip1_audio,
        generate_silence(0.25),
        clip2_audio,
        generate_silence(3.0),       # ✅ 3-second pause here
        tts3_audio,
        generate_silence(0.25),
        tts4_audio,
        generate_silence(1.0)
    ])
    full_audio = full_audio.set_duration(full_audio.duration)

    # --- VIDEO CLIPS TO MATCH AUDIO --------------------------------------------
    clip1_duration = clip1_audio.duration + 0.25
    clip1 = ImageClip(static_img).set_duration(clip1_duration)
    clip2 = ImageClip(static_img).set_duration(clip2_audio.duration)

    frame_clips = [ImageClip(p).set_duration(FRAME_DURATION) for p in frame_paths]
    chart_animation = concatenate_videoclips(frame_clips, method="compose")
    chart_animation_duration = chart_animation.duration

    total_audio_duration = full_audio.duration
    remaining_duration = total_audio_duration - (clip1_duration + clip2.duration + chart_animation_duration)

    last_chart_frame = frame_paths[-1]
    freeze_frame_duration = max(remaining_duration, tts4_audio.duration + 0.5)
    freeze_frame_clip = ImageClip(last_chart_frame).set_duration(freeze_frame_duration)

    # --- STITCH FINAL VIDEO ----------------------------------------------------
    clips = [clip1, clip2, chart_animation, freeze_frame_clip]
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(full_audio.set_duration(final_video.duration))

    # --- CAPTIONS --------------------------------------------------------------
    video_size = final_video.size
    caption_clips = []

    current_time = 0
    caption_clips.append(make_timed_caption_clip(string1, current_time, clip1_audio.duration, video_size))
    current_time += clip1_audio.duration + 0.25

    caption_clips.append(make_timed_caption_clip(string2, current_time, clip2_audio.duration, video_size))
    current_time += clip2_audio.duration + 3.0  # ✅ 3-second pause included here

    caption_clips.append(make_timed_caption_clip(string3, current_time, tts3_audio.duration, video_size))
    current_time += tts3_audio.duration + 0.25

    caption_clips.append(make_timed_caption_clip(string4, current_time, tts4_audio.duration, video_size))

    # --- EXPORT INTERMEDIATE VIDEO ---------------------------------------------
    intermediate_video_path = "intermediate_video.mp4"
    final_video.write_videofile(intermediate_video_path, fps=15)
    print("✅ Intermediate video exported successfully.")

    # --- ADD TEXT & OVERLAY ----------------------------------------------------
    overlay_text = f"{symbol} [{tf_key}]\nMT5 bot Link:\nlinktr.ee/WannaBeQuant"
    temp_video = VideoFileClip(intermediate_video_path)

    rainbow_overlay_clip = get_rainbow_overlay_clip(
        text=overlay_text,
        duration=temp_video.duration,
        video_size=temp_video.size
    )

    final_video_with_overlay = CompositeVideoClip(
        [temp_video, rainbow_overlay_clip] + caption_clips
    )
    final_video_with_overlay.write_videofile(output_path, fps=15)

    print("✅ Final video with text overlay and captions exported successfully.")



import time
import schedule
import os
import logging
from pathlib import Path

# Your function definitions (assumed to exist)
# from your_module import generate_trading_video, yt_video, upload_to_tiktok, insta_video

VIDEO_DIR = Path("generated_videos")
VIDEO_FILENAME = "final_video_with_overlay.mp4"
VIDEO_PATH = VIDEO_DIR / VIDEO_FILENAME
DESCRIPTION = "trading game! #tradingforex #forexstrategy #cryptotrading #tradingcrypto #bitcoin #forextrading #stocks"
COOKIES_FILE = "cookies2.txt"

def ensure_folder():
    VIDEO_DIR.mkdir(exist_ok=True)

def create_video_if_not_exists():
    if not VIDEO_PATH.exists():
        logging.info("Generating video...")
        generate_trading_video(output_path=str(VIDEO_PATH))
    else:
        logging.info("Video already exists, using existing file.")


def main():
    logging.basicConfig(level=logging.INFO)
    ensure_folder()
    create_video_if_not_exists()

    if not VIDEO_PATH.exists():
        logging.critical("Video was not generated or is missing.")
        return


def job():
    gc.collect()
    print("🕒 Starting scheduled job...")
    main()

if __name__ == "__main__":
    print("✅ Scheduler started")
    
    # Run once immediately
    job()
    
    # Schedule to run every 8 hours
    schedule.every(8).hours.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute