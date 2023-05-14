"""
6.101 Spring '23 Lab 0: Audio Processing
"""
# No additional imports allowed!
import wave
import struct


def backwards(sound):
    """
    Creates a new sound file and modifies it to return a backwards
    sampled sound piece.
    """
    new_sound = {"rate": sound["rate"], "samples": sound["samples"][::-1]}
    return new_sound


def interpolate(list1, list2, weight):
    """
    Interpolates between two lists according to weight.
        elem[i] = weight*list1[i] + (1-weight)*list2[i]

    Args:
        list1: An array-like structure
        list2: An array-like structure
        weight: The amount of list1 to prioritize in the interpolation
    """
    return [weight*elem1 + (1-weight)*elem2 for elem1, elem2 in zip(list1, list2)]


def mix(sound1, sound2, s1_weight):
    """
    Mixes together two sound bites at a given percentage. More formally,
    given two sets of samples representing music, samp1, samp2:
        out_sample = s1_weight * sound1_sample + (1-s1_weight) * sound2_sample

    Args:
        sound1: A mono sound dictionary with two key/value pairs:
            * "rate": an int representing the sampling rate, samples per second
            * "samples": a list of floats containing the sampled values
        sound2: A mono sound dictionary with two key/value pairs (as above)
        s1_weight: The weighing to apply to the first sound file.

    Returns:
        A new mono sound dictionary.
    """
    if (
        "rate" not in sound1.keys()
        or "rate" not in sound2.keys()
        or sound1["rate"] != sound2["rate"]
    ):
        return None

    rate = sound1["rate"]  # get rate
    if "samples" in sound1: # mono files
        min_len = min(len(sound1["samples"]), len(sound2["samples"]))
        out_sample = interpolate(sound1["samples"][:min_len], sound2["samples"][:min_len], s1_weight)
        newWav = {"rate": rate, "samples": out_sample}
    else: # stereo files
        min_len = min(len(sound1["left"]), len(sound2["left"]))
        out_sampleL = interpolate(sound1["left"][:min_len], sound2["left"][:min_len], s1_weight)
        out_sampleR = interpolate(sound1["right"][:min_len], sound2["right"][:min_len], s1_weight)
        newWav = {"rate": rate, "left": out_sampleL, "right": out_sampleR}

    return  newWav # return new sound


def convolve(sound, kernel):
    """
    Applies a filter to a sound, resulting in a new sound that is longer than
    the original mono sound by the length of the kernel - 1.
    Does not modify inputs.

    Args:
        sound: A mono sound dictionary with two key/value pairs:
            * "rate": an int representing the sampling rate, samples per second
            * "samples": a list of floats containing the sampled values
        kernel: A list of numbers

    Returns:
        A new mono sound dictionary.
    """
    final_sample = [0]*(len(sound["samples"]) + len(kernel) - 1)

    # running offset sum (convolution)
    for offset, scale in enumerate(kernel):
        # short circuit any zero vals to speed up process
        if scale == 0:
            continue

        for curInd, sample in enumerate(sound["samples"]):
            final_sample[offset + curInd] += scale * sample

    return {"rate": sound["rate"], "samples": final_sample}


def echo(sound, num_echoes, delay, scale):
    """
    Compute a new signal consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
        scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """
    delay_n = round(delay * sound["rate"])
    echo_filter = [0] * (delay_n * num_echoes + 1)
    for i in range(num_echoes + 1):
        offset = i * delay_n
        echo_filter[offset] = scale ** i

    return convolve(sound, echo_filter)


def pan(sound):
    """
    Performs a pan operation on a streo sound wav file and returns
    a new wav sound with the panning applied.

    Args:
        sound: a stereo sound dictionary to manipulate
    """
    # Create list with relevant mangitudes to apply to the channels
    num_samples = len(sound["left"])
    mag_list = [ind/(num_samples-1) for ind in range(num_samples)]
    new_sound = {'rate':sound['rate'], 
                'left':sound['left'].copy(), 
                'right':sound['right'].copy()}

    # And then apply to each channel
    for ind in range(num_samples):
        new_sound['right'][ind] *= mag_list[ind]
        new_sound['left'][ind] *= 1 - mag_list[ind]

    return new_sound


def remove_vocals(sound):
    """
    Attempts to remove the vocals from a wav file by subtracting the common
    audio between channels. Returns a new mono wav sound with the difference
    (often only leaves instruments which are manipulated to be channel-specific)

    Args:
        sound: a mono sound dictionary potentially without vocals
    """
    # Acquire some simple metadata and make the output copy
    num_samples = len(sound["left"])
    new_samples = list()
    
    # Perform algorithm
    for ind in range(num_samples):
        new_samples.append(sound['left'][ind]-sound['right'][ind])
    
    return {'rate':sound['rate'], 'samples':new_samples}


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def bass_boost_kernel(boost, scale=0):
    """
    Constructs a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.

    Args:
        boost: an int that controls the frequencies that are boosted (0 will
            boost all frequencies roughly equally, and larger values allow more
            focus on the lowest frequencies in the input sound).
        scale: a float, default value of 0 means no boosting at all, and larger
            values boost the low-frequency content more);

    Returns:
        A list of floats representing a bass boost kernel.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    kernel = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    for i in range(boost):
        kernel = convolve(kernel, base["samples"])
    kernel = kernel["samples"]

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel) // 2] += 1

    return kernel


def load_wav(filename, stereo=False):
    """
    Load a file and return a sound dictionary.

    Args:
        filename: string ending in '.wav' representing the sound file
        stereo: bool, by default sound is loaded as mono, if True sound will
            have left and right stereo channels.

    Returns:
        A dictionary representing that sound.
    """
    sound_file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = sound_file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    left = []
    right = []
    for i in range(count):
        frame = sound_file.readframes(1)
        if chan == 2:
            left.append(struct.unpack("<h", frame[:2])[0])
            right.append(struct.unpack("<h", frame[2:])[0])
        else:
            datum = struct.unpack("<h", frame)[0]
            left.append(datum)
            right.append(datum)

    if stereo:
        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = [(ls + rs) / 2 for ls, rs in zip(left, right)]
        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Save sound to filename location in a WAV format.

    Args:
        sound: a mono or stereo sound dictionary
        filename: a string ending in .WAV representing the file location to
            save the sound in
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l_val, r_val in zip(sound["left"], sound["right"]):
            l_val = int(max(-1, min(1, l_val)) * (2**15 - 1))
            r_val = int(max(-1, min(1, r_val)) * (2**15 - 1))
            out.append(l_val)
            out.append(r_val)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # Evaluate mystery sound and save it
    print("Evaluating secret.wav...")
    secret = load_wav("sounds/mystery.wav")
    write_wav(backwards(secret), "sounds/mystery_reversed.wav")

    # Perform bass-boosting
    print("Performing bass boosting on chilli.wav...")
    chillWav = load_wav("sounds/ice_and_chilli.wav")
    write_wav(convolve(chillWav, bass_boost_kernel(1000, 1.5)), "sounds/bass_boosted_chilli.wav")

    # Now perform echo manipulation on chord
    print("Performing echo on chord.wav...")
    cordWav = load_wav("sounds/chord.wav")
    write_wav(echo(cordWav, 5, 0.3, 0.6), "sounds/echo_chord.wav")