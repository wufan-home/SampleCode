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

### Step 2: Install the script
Download the script https://github.com/wufan-home/SampleCode/blob/master/tools/youtube_transcript/get_transcript.py to the folder `~/youtube_transcript`.

**Syntax**:
```
python3 ~/youtube_transcript/get_transcript.py --url "<URL>" --output_dir ~/Downloads
```

**Sample**:
```
python3 ~/youtube_transcript/get_transcript.py \
--url "https://www.youtube.com/watch?v=MIJFyUPG4Z4&list=PL5q3E8eRUieWtYLmRU3z94-vGRcwKr9tM&index=7&pp=iAQB" \
--output_dir ~/Downloads
```

**Sample output**:
```
Transcript written to /Users/fanwu/Downloads/Design_a_Distributed_Rate_Limiter_w_a_Ex_Meta_Staff_Engineer_System_Design_Breakdown.md
```

### Step 3: Use AI to Understand the Script
Use the following prompt:
```
翻译 /Users/fanwu/Downloads/Design_a_Distributed_Rate_Limiter_w_a_Ex_Meta_Staff_Engineer_System_Design_Breakdown.md z至中文。然后总结思维导图。要求：从左到右展开
```
