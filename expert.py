"""
Usage: python expert.py <audio file>
"""

import sys
import os

from pydub import AudioSegment
import matplotlib.pyplot as plt

from audio_to_midi_melodia import audio_to_midi_melodia as atmm
from pyin import pyin_getnotes as pyin

PROTO_PATTERN = [2, 4, 5, 7, 4, 0, 2] # the prototypical pattern of the pitches of The Lick

YES_MSG = "The Lick"
NO_MSG = "Not The Lick"

def ascending(nums):
    for i, _ in enumerate(nums):
        if i == 0:
            continue
        if nums[i] < nums[i-1]:
            return False
    
    return True

def descending(nums):
    for i, _ in enumerate(nums):
        if i == 0:
            continue
        
        if nums[i] > nums[i-1]:
            return False
        
        return True

def desc_approx(nums, threshold=1):
    """
    returns whether the given numbers descend with an allowance for a number of deviations from that (the threshold)

    So, for a threshold of 0, descending would require strict descent. nums[i-1] > nums[i] for all  i > 0
    But for a threshold of 1, the following would still approximately descend:

    4,2,3,1

    Since there is only one pair of numbers that does not follow the descending rule
    """

    asc_count = 0

    for i, _ in enumerate(nums):
        if i == 0: continue
        asc_count += 1 if nums[i] > nums[i-1] else 0
    
    print(f"{asc_count=}")

    return asc_count <= threshold


## new idea:
"""
what if you looked for the pitch contour of the lick kind of like how I search for char patterns in PyProfanity?
and if you keep a count of how many extra (grace) notes come up, you can cut it off according to that
"""


def is_lick(notes):
    pitches = [int(z) for _, _, z in notes]
    min_pitch = min(pitches)
    
    # normalize pitches so the lowest is 0
    pitches = [x - min_pitch for x in pitches]
    # print(f"pitches: {pitches}")
    
    if len(pitches) < 6:
        return False
    elif len(pitches) == 6:
        # if it has 6 notes, there are only a couple options
        possible_patterns = [
            [4, 5, 7, 4, 0, 2], # scale degrees 3 4 5 3 1 2
            [2, 4, 5, 7, 0, 2]  # scale degrees 2 3 4 5 1 2
        ]

        for pattern in possible_patterns:
            if pitches == pattern:
                return True
        
        return False
    elif len(pitches) == 7:
        # if it has 7 notes, it better be 2 3 4 5 3 1 2
        # TODO but it could also be something close to this but not exactly?
        if pitches == PROTO_PATTERN:
            return True
        
        if not abs(pitches[-1] - pitches[0]) <= 1:
            return False

        # last four notes must follow the general pattern of highest, second highest, lowest, second lowest
        w, x, y, z = pitches[-4:]
        return w > x and w > y and w > z and y < z and x > z
    elif len(pitches) == 8:
        # if the first 5 notes are all ascending, treat the first note as a grace note
        # check that the tones after the first 4 or 5 follow on-net a steeper, negative slope
        if ascending(pitches[:5]):
            if pitches[1:] == PROTO_PATTERN:
                return True
            
            # if the first note of the lick, excluding the grace note, and the last note of the lick are within 1 semitone
            if not abs(pitches[-1] - pitches[1]) <= 1:
                return False

            # if the ascending line is correct and the line descends afterward, plus the above guard clause passed
            return pitches[1:5] == PROTO_PATTERN[0:4] and descending(pitches[5:8])
        elif ascending(pitches[:4]):
            # must be a grace note somewhere else
            if not abs(pitches[-1] - pitches[0]) <= 1:
                return False
            
            # check for a grace note into the second to last note of the lick
            # as in, 2 3 4 5 2-3 1 2
            # check for the middle notes of the ideally 5 2 3 1 sequence being in between the 5 and the 1
            w, x, y, z = pitches[3:7]
            return w > x and w > y and x > z and y > z

    print("\twe didn't find anything wow")
    return False


def classify(audio_file, show_graphic=False):
    # notes is a list of tuples that have the form (note_start_time, note_length, note_pitch)
    a_s = AudioSegment.from_file(audio_file)

    length = len(a_s) / 1000 # in seconds

    # print(f"minduration: ", length/30)

    melodia_notes = atmm(audio_file, minduration=length/50)
    pyin_notes = pyin(audio_file)
    # print(notes)

    is_lick_melodia = is_lick(melodia_notes)
    is_lick_pyin = is_lick(pyin_notes)
 
    ans = YES_MSG if is_lick_melodia or is_lick_pyin else NO_MSG

    notes = pyin_notes if is_lick_pyin else melodia_notes
    # notes = melodia_notes if is_lick_melodia else pyin_notes

    # start times and note values
    xs = [x for x, _, _ in notes]
    ys = [z for _, _, z in notes]

    # add the duration for the final note
    ys.append(ys[-1])
    xs.append(xs[-1] + notes[-1][1])

    if show_graphic:
        plt.hlines(ys[:-1], xs[:-1], xs[1:], linewidth=15) # kind of close to looking like midi lol
        plt.title(ans)
        plt.show()
    else:
        print(f"{audio_file}: {ans}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python expert.py <audio file>")
        exit(0)

    if os.path.isdir(sys.argv[1]):
        directory = sys.argv[1]

        alphabetical_items = sorted(os.listdir(directory))

        for item in alphabetical_items:
            classify(f"{directory}/{item}", show_graphic=False)
    else:
        classify(sys.argv[1], show_graphic=True)


if __name__ == "__main__":
    main()