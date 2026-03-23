"""
Split Video by Keyword in Subtitles
Extracts video segments containing specific keywords from subtitle file
Uses MoviePy for video editing and regex for text matching
"""
import re

def convert_time(timestring):
    """
    Converts subtitle timestamp string to seconds
    Format: HH:MM:SS.mmm
    """
    nums= list(map(float, re.findall(r'\d+', timestring)))
    return 3600*nums[0] + 60*nums[1] + nums[2] + nums[3]/1000

#you.en.srt   
#state.en.srt
with open("C:/Users/muosa/Desktop/1-StartWork/Youtube-dl/you.en.srt ") as f:
    lines = f.readlines()
    
times_texts = []
current_times , current_text = None, ""
for line in lines:
    # look at appendix to explain the regular expression
    times = re.findall('[0-9]*:[0-9]*:[0-9]*.[0-9]*', line) 
    if times != []:
        current_times = list(map(convert_time, times))
    elif line == '\n':
        times_texts.append((current_times, current_text))
        current_times, current_text = None, ""
        
    elif current_times is not None:
        current_text = current_text + line.replace("\n"," ")
    
#print (times_texts )
for tim in times_texts :
    print (tim)
    
from collections import Counter
whole_text = " ".join([text for (time, text) in times_texts])
all_words = re.findall("\w+", whole_text)
counter = Counter([w.lower() for w in all_words if len(w)>5])
print (counter.most_common(10))
cuts = [times for (times,text) in times_texts
        if (re.findall("enemies",text) != [])] 
for cu in cuts :
    print (cu )
from moviepy.editor import VideoFileClip, concatenate
video = VideoFileClip("C:/Users/muosa/Desktop/1-StartWork/Youtube-dl/You.mp4 ")

def assemble_cuts(cuts, outputfile):
    """
    Concatenate video cuts and generate output video file
    Args:
        cuts: List of (start_time, end_time) tuples
        outputfile: Path for output video
    """
    final = concatenate([video.subclip(start, end) for (start,end) in cuts])
    final.to_videofile(outputfile)

assemble_cuts(cuts, "C:/Users/muosa/Desktop/1-StartWork/Youtube-dl/41.mp4")
times, texts = zip(*times_texts)
txt_lengths = list(map(len, texts)) # length of each subtitle block
indices = [sum(txt_lengths[:i]) for i in range(len(texts))]

def find_times(position):
    """
    Finds the (t_start, t_end) in the subtitles for a given position in the whole text
    Args:
        position: Character position in concatenated text
    Returns:
        Tuple of (start_time, end_time)
    """
    return times[ max([i for i in range(len(indices))
                       if (indices[i] <= position)])]

# Regular expression matching all sentences with 'word'
regexpr = "([A-Z][^\.!?]*%s[^\.!?]*[\.!?])"%("enemies ")
cuts = [ (find_times(m.start())[0], find_times(m.end())[1])
         for m in re.finditer(regexpr, whole_text) ]
assemble_cuts(cuts, "C:/Users/muosa/Desktop/1-StartWork/Youtube-dl/erer.mp4")
