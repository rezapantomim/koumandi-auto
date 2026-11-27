import { loadFont } from '@remotion/google-fonts/Vazirmatn';

// Vazirmatn: Persian + Latin in one family (headings use the heavy weight)
const fam = loadFont('normal', { weights: ['400', '600', '800', '900'], subsets: ['arabic', 'latin'] }).fontFamily;
export const HEAD = fam;
export const BODY = fam;
