import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import flipspire as a
class Tests(unittest.TestCase):
 def test_launch(self):
  g=a.Table();self.assertTrue(g.launch());self.assertFalse(g.launch());self.assertEqual(g.used[0],1);self.assertLess(g.vy,0)
 def test_three_balls(self):
  g=a.Table()
  for _ in range(3):self.assertTrue(g.launch());g.drain()
  self.assertTrue(g.over);self.assertFalse(g.launch())
 def test_bumper(self):
  g=a.Table();g.launch();g.x=19;g.y=14;g.vx=0;g.vy=-10;g.step(.01);self.assertEqual(g.scores[0],50);g.step(.01);self.assertEqual(g.scores[0],50)
 def test_left_flipper(self):
  g=a.Table();g.launch();g.x=23;g.y=32.5;g.vy=10;g.vx=0;g.step(.01,True,False);self.assertLess(g.vy,0);self.assertGreater(g.vx,0)
 def test_right_flipper(self):
  g=a.Table();g.launch();g.x=37;g.y=32.5;g.vy=10;g.vx=0;g.step(.01,False,True);self.assertLess(g.vy,0);self.assertLess(g.vx,0)
 def test_wall(self):
  g=a.Table();g.launch();g.x=1;g.vx=-5;g.y=10;g.step(.01);self.assertGreater(g.vx,0)
 def test_target(self):
  g=a.Table();g.launch();g.x=12;g.y=4;g.vx=0;g.vy=-2;g.step(.01);self.assertEqual(g.scores[0],100)
 def test_drain(self):
  g=a.Table();g.launch();g.y=41;g.step(.01);self.assertFalse(g.ball);self.assertFalse(g.over)
 def test_records(self):
  with tempfile.TemporaryDirectory() as d,patch.object(a,'RECORDS',Path(d)/'r.json'):
   g=a.Table();g.scores[0]=123;self.assertTrue(a.save_records(g));self.assertEqual(a.load_records()['best'],123)
 def test_simulation_finite(self):
  import math
  g=a.Table();g.launch()
  for _ in range(5000):
   g.step(.03,True,True)
   if not g.ball:break
  self.assertTrue(all(math.isfinite(v) for v in (g.x,g.y,g.vx,g.vy)))
if __name__=='__main__':unittest.main()
