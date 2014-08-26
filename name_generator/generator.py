#! /usr/bin/env python3

from collections import defaultdict
import random

def GetNames(fname):
  with open(fname, 'r') as fin:
    names = [name.strip().lower() for name in fin.readlines()]
    return names

class WordGenerator(object):
  ''' Generates words using statistical properties of the given list of seed
  words.
  '''

  def __init__(self, words):
    self.positional_freqs = self._CalcCharFreqs(words)

  def GenerateWord(self):
    ''' Generates a word by walking a markov chain where priors are taken from
    the current character index in the word and the last generated character,
    and the next character is chosen probabilistically using the frequencies of
    that that character comes after the current character in the current
    position.
    '''
    cur_pos = 0
    cur_char = self._ChooseNext(self.positional_freqs[0]['^'])

    chars = []
    while cur_char != '$':
      chars.append(cur_char)
      cur_pos += 1
      cur_char = self._ChooseNext(self.positional_freqs[cur_pos][cur_char])

    return ''.join(chars)

  def _CalcCharFreqs(self, words):
    # map of positional index in word
    #   -> map of current character
    #   -> map of next possible character
    #   -> count of times next possible character appeared in list of words
    positional_counts = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float)))

    # TODO the special characters '^' and '$' denote the beginning and end of a
    # word respectively. This is done so that I don't have to keep track of
    # frequency distributions for the first character and the last character in
    # a word seperately. That said, this isn't a great solution because it
    # creates forbidden characters in the words.
    for word in words:
      character_pairs = zip('^' + word, word + '$')
      for pos, (char, char_after) in enumerate(character_pairs):
        positional_counts[pos][char][char_after] += 1

    # Normalize character counts so that the sum of all after-character
    # frequencies for a given position and current-character is equal to 1.
    for character_counts in positional_counts.values():
      for next_char_freqs in character_counts.values():
        norm_factor = sum(next_char_freqs.values())
        for char, freq in next_char_freqs.items():
          next_char_freqs[char] = float(freq) / norm_factor

    return positional_counts

  def _ChooseNext(self, freqs):
    probability = random.random()

    cum_probability = 0
    for next_char, freq in freqs.items():
      cum_probability += freq
      if probability <= cum_probability:
        return next_char

    # This should never happen theoretically because the sum of all frequencies
    # should be one, but rounding errors might cause this to occur.
    return next_char


def main():
  first_names = GetNames('names/first-en.txt')
  first_name_generator = WordGenerator(first_names)
  rand_names = [first_name_generator.GenerateWord() for i in range(100)]
  common_names = set(n for n in rand_names) & set(n for n in first_names)
  print("Seeded with %d real names" % len(first_names))
  print("Generated %d names" % len(rand_names))
  real_name_ratio = len(common_names) / len(rand_names)
  print("%d generated names are real (%g%%)" %
        (len(common_names), real_name_ratio))
  print("Real names which were also generated: %s" % common_names)
  print("Generated names: %s" % rand_names)

if __name__ == '__main__':
  main()
