import collections
from hypothesis import given, strategies as st
import unittest

def is_message_from_magazine_brute_force(message: str, magazine: str) -> bool:
    # An empty message is always constructible, regardless of the magazine.
    if not message:
        return True

    for c in message:
        # Find the first occurrence of the letter in the magazine.
        i = magazine.find(c)
        if i == -1:
            return False
        # Remove found letter from magazine. "Cut" it out of the magazine.
        magazine = magazine[:i] + magazine[i+1:]

    return True
def is_message_from_magazine_optimal(message: str, magazine: str) -> bool:
    if not message:
        return True

    # Build up character frequency hash table for input message.
    message_char_freq = collections.Counter(message)

    for c in magazine:
        if c in message_char_freq:
            message_char_freq[c] -= 1
            if message_char_freq[c] == 0:
                # Remove this key to speed up subsequent lookups into
                # message_char_freq.
                del message_char_freq[c]
                # If the hash table becomes empty, we're done!
                if not message_char_freq:
                    return True

    return False
def is_message_from_magazine_pythonic(message: str, magazine: str) -> bool:
    if not message:
        return True

    return (not collections.Counter(message) -
            collections.Counter(magazine))

class Test(unittest.TestCase):
    def test_basic(self):
        # Empty inputs.
        message = ""
        magazine = ""
        result = is_message_from_magazine_brute_force(message, magazine)
        self.assertEqual(result, True)

        # Basic examples, as described in the problem statement.
        message = "hello"
        magazine = "old"
        result = is_message_from_magazine_brute_force(message, magazine)
        self.assertEqual(result, False)
        message = "hello"
        magazine = "old elf hat"
        result = is_message_from_magazine_brute_force(message, magazine)
        self.assertEqual(result, True)
    @given(st.text(max_size=20), st.text(max_size=100))
    def test_random(self, message: str, magazine: str):
        result_bf = is_message_from_magazine_brute_force(message, magazine)
        result_optimal = is_message_from_magazine_optimal(message, magazine)
        result_pythonic = is_message_from_magazine_pythonic(message, magazine)

        # Do the solutions agree with each other?
        self.assertEqual(result_bf, result_optimal)
        self.assertEqual(result_optimal, result_pythonic)

if __name__ == "__main__":
    unittest.main(exit=False)
