import os
import glob
import shutil
import subprocess
import argparse
from pydub import AudioSegment
from pydub.utils import make_chunks
from scipy.io import wavfile
from matplotlib import pyplot as plt
from PIL import Image


def mp3towav(path):
    folders=glob.glob(path+'*')
    #print "folders",folders
    for folder in folders:
      files = glob.glob(folder+'/'+ '*.mp3')
      #print files
      if len(files) == 0:
          return 10
      for file in files:
          mp = file
          wa = file.replace('mp3', 'wav')
          try:
            print("Converting using sox")
            subprocess.call(['sox', mp, '-e', 'mu-law', '-r', '16k', wa, 'remix', '1,2'])
          except Exception as e:
            print("Converting using ffmpeg")
            try:
              subprocess.call('ffmpeg -i %s -acodec pcm_s16le -ac 1 -ar 16000 %s' %(mp,wa),shell=True)
            except Exception as e:
              print("Error while converting: "+str(e))  

def makechunks(path):
    folders=glob.glob(path+'*')
    for folder in folders:
      waves = glob.glob(folder+'/'+ '*.wav')
      print 'w',waves
      if len(waves) == 0:
          return 10
      for i in waves:
          w = i
          myaudio = AudioSegment.from_file(i, 'wav')
          chunk_length_ms = 20000
          chunks = make_chunks(myaudio, chunk_length_ms)
          print chunks
          for i, chunk in enumerate(chunks):
              chunk_name = w.split('.')[0] + "chunk{0}.wav".format(i)
              print chunk_name
              print "exporting", chunk_name
              chunk.export(folder+'/'+chunk_name, format="wav")


def graph_spectrogram(wav_file):
    rate, data = get_wav_info(wav_file)
    print type(data), len(data)
    nfft = 256  # Length of the windowing segments
    fs = 256  # Sampling frequency
    pxx, freqs, bins, im = plt.specgram(data, nfft, fs)
    print "pxx : ", len(pxx)
    print "freqs : ", len(freqs)
    print "bins : ", len(bins)
    # plt.axis('on')
    # plt.show()
    plt.axis('off')
    print wav_file.split('.wav')[0]
    plt.savefig(wav_file.split('.wav')[0] + '.png',
                dpi=100,  # Dots per inch
                frameon='false',
                aspect='normal',
                bbox_inches='tight',
                pad_inches=0)  # Spectrogram saved as a .png
    try:
      im = Image.open(wav_file.split('.wav')[0] + '.png')
      rgb_im = im.convert('RGB')
      rgb_im.save(wav_file.split('.png')[0] + '.jpg')
    except Exception as e:
      print e
    if os.path.exists(wav_file.split('.wav')[0] + '.png'):
        os.system('convert '+(wav_file.split('.wav')[0] + '.png') + ' '+(wav_file.split('.wav')[0] + '.jpg'))
        os.remove(wav_file.split('.wav')[0] + '.png')


def get_wav_info(wav_file):
    rate, data = wavfile.read(wav_file)
    return rate, data


def wav2spectrogram(path):
    folders = glob.glob(path+'*')
    for folder in folders:
      waves = glob.glob(folder+'/' + '*.wav')
      print waves
      if len(waves) == 0:
        return 10
      for f in waves:
        try:
            print "Generating spectrograms.."
            graph_spectrogram(f)
        except Exception as e:
            print "Something went wrong while generating spectrogram: ", e

def move_images(path):
    folders = glob.glob('*')
    for folder in folders:
        os.makedirs('../tf_files/data_image/'+folder)
        waves=glob.glob('*.jpg')
        print waves
        for wav in waves:
            shutil.move(path+folder+'/'+wav,'../tf_files/data_image/'+folder+'/'+wav)


if __name__ == '__main__':
    path='../tf_files/data_audio/'
    parser = argparse.ArgumentParser()
    #parser.add_argument('path', help="Specify the path to the music directory", default="../tf_files/data_mp3/")
    parser.add_argument('--mkchunks', help="Set this flag if you want to make chunks of waves", action="store_true", default=True)
    parser.add_argument('--mp3towav', help="Set this flag if you want to convert mp3 to wav", action="store_true",default=True)
    parser.add_argument('--spectrogram', help="Set this flags  to create spectrograms", action="store_true",default=True)
    args = parser.parse_args()
    if args.mp3towav:
        print
        "Path : ", path
        try:
            r = mp3towav(path)
            if r == 10:
                print
                "No mp3 files in specified directory"
            else:
                print
                "All mp3 files processed completely"
        except Exception as e:
            print
            "Something went wrong :", e
    if args.mkchunks:
        print
        "Searching for wav files in :", path
        try:
            r = makechunks(path)
            if r == 10:
                print
                "No wav files in given path"
            else:
                print
                "Completed successfully"
        except Exception as e:
            print
            "Something went wrong : ", e
    if args.spectrogram:
        print "Finding files in : ", path
        try:
            r = wav2spectrogram(path)
            if r == 10:
                print "No wav files found in the given path"
            else:
                move_images(path)
                print "All mp3 files processed completely"
        except Exception as e:
            move_images(path)
            print "Something went wrong: ", e
