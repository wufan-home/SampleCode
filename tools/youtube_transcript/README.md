The script can download the transcript of a youtube video.

## Usage

### Step 1: Set up the Python venv

**Note**: The script is written in Python 3.14.

Create the venv through Python 3.14:
```
mkdir -p ~/youtube_transcript/venv
python3.14 -m venv ~/youtube_transcript/venv
source ~/youtube_transcript/venv/bin/activate
```

Install the youtube API modulo to the virtual environment:
```
pip3 install youtube-transcript-api
```

### Step 2: Download the script
**Syntax**:
```
python3 ./get_transcript.py --url "<URL>" --output_dir ~/Downloads
```

**Sample**:
```
python3 ./get_transcript.py \
--url "https://www.youtube.com/watch?v=MIJFyUPG4Z4&list=PL5q3E8eRUieWtYLmRU3z94-vGRcwKr9tM&index=7&pp=iAQB" \
--output_dir ~/Downloads
```
