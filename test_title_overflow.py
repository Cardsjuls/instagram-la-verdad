import unittest
from PIL import Image, ImageDraw
import degradado_hola as renderer

class TitleOverflowTests(unittest.TestCase):
    def setUp(self):
        self.draw = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
        self.font = renderer.find_font(100)

    def fit(self, text, width=700, height=270):
        lines = renderer._fit_title_lines(self.draw, text, self.font, -1, 4, .65, .88, width, height)
        layers = [renderer._render_line_image(line, self.font, -1, 4) for line in lines]
        step = int(layers[0].height * .88)
        self.assertLessEqual(max(int(layer.width * .65) for layer in layers), width)
        self.assertLessEqual(max(i * step + layer.height for i, layer in enumerate(layers)), height)
        return lines

    def test_short_title_unchanged(self):
        self.assertEqual(' '.join(self.fit('PUTIN ACEPTA LA PAZ')), 'PUTIN ACEPTA LA PAZ')

    def test_long_title_keeps_whole_words(self):
        title = 'ANMEPRO RESPALDA EL PROYECTO DE LEY MIRABAL Y DESTACA SU APORTE A LA PROTECCION LABORAL ' * 20
        result = ' '.join(self.fit(title))
        self.assertTrue(result.endswith('...'))
        self.assertTrue(title.startswith(result[:-3]))
        self.assertIn(result[:-3].split()[-1], title.split())

    def test_single_overlong_word(self):
        self.assertEqual(self.fit('W' * 500), ['...'])

    def test_explicit_line_breaks_that_fit(self):
        self.assertEqual(self.fit('PAZ\nCON UCRANIA'), ['PAZ', 'CON UCRANIA'])

    def test_area_too_small_is_explicit_error(self):
        with self.assertRaises(ValueError):
            self.fit('TITULAR', width=1, height=1)

if __name__ == '__main__':
    unittest.main()
