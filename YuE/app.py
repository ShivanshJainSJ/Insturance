import warnings

from audiocraft.data.audio import audio_write
from audiocraft.models import MusicGen

warnings.filterwarnings("ignore", category=UserWarning)

print("Loaded")

def load_model():
    model = MusicGen.get_pretrained('facebook/musicgen-small')
    return model

def generate_music_tensors(description, duration: int):
    print("Description: ", description)
    print("Duration: ", duration)
    model = load_model()
    model.set_generation_params(duration=duration)
    wav = model.generate([description])

    return wav, model.sample_rate

def main():
    print("Text to Music Generator")

    description = input("Enter your description: ")
    time = int(input("Select time duration (In Seconds): "))

    if description and time:
        proceed = input("Generate music? (yes/no): ")
        if proceed.lower() == 'yes':
            print("Generating music .....")
            wav, sample_rate = generate_music_tensors(description, time)
            print("Saving generated music .....")
            file_path = f"audios/{description.replace(' ', '_')}"
            for idx, one_wav in enumerate(wav):
                audio_write(file_path, one_wav.cpu(), sample_rate, strategy="loudness", loudness_compressor=True)
            print(f"Music saved as {file_path}")

if __name__ == "__main__":
    main()