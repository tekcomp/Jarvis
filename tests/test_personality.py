import unittest
from core.personality_engine_v2 import get_engine, PersonalityState

class TestPersonalityEngine(unittest.TestCase):
    def test_default_state(self):
        personality = get_engine()
        self.assertEqual(personality.state.mode, "assistant")
        self.assertEqual(personality.state.mood, "positive")
        self.assertEqual(personality.state.emotion, "excited")
        self.assertEqual(personality.state.emotion_strength, 1.0)

    def test_reset_state(self):
        personality = get_engine()
        personality.update("hello world")
        personality.reset()
        self.assertEqual(personality.state.mode, "assistant")
        self.assertEqual(personality.state.mood, "positive")
        self.assertEqual(personality.state.emotion, "excited")
        self.assertEqual(personality.state.emotion_strength, 1.0)

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)