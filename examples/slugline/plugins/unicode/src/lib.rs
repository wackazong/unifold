//! A transliteration plug-in for Latin letters with diacritics.
//!
//! ```
//! use slugline_core::{slugify_with, Options};
//! use slugline_unicode::Latin;
//! assert_eq!(slugify_with("Crème brûlée", &Options::default(), &Latin), "creme-brulee");
//! ```

use slugline_core::Transliterate;

/// Maps the letters of Latin-1 Supplement and Latin Extended-A to their base
/// letters, and ligatures to two letters. It does not know any other script.
pub struct Latin;

impl Transliterate for Latin {
    fn transliterate(&self, c: char) -> Option<&str> {
        Some(match c {
            'À'..='Å' | 'à'..='å' | 'Ā'..='ą' => "a",
            'Æ' | 'æ' => "ae",
            'Ç' | 'ç' | 'Ć'..='č' => "c",
            'Ð' | 'ð' | 'Ď'..='đ' => "d",
            'È'..='Ë' | 'è'..='ë' | 'Ē'..='ě' => "e",
            'Ĝ'..='ģ' => "g",
            'Ĥ'..='ħ' => "h",
            'Ì'..='Ï' | 'ì'..='ï' | 'Ĩ'..='ı' => "i",
            'Ĳ' | 'ĳ' => "ij",
            'Ĵ' | 'ĵ' => "j",
            'Ķ'..='ĸ' => "k",
            'Ĺ'..='ł' => "l",
            'Ñ' | 'ñ' | 'Ń'..='ŋ' => "n",
            'Ò'..='Ö' | 'Ø' | 'ò'..='ö' | 'ø' | 'Ō'..='ő' => "o",
            'Œ' | 'œ' => "oe",
            'Ŕ'..='ř' => "r",
            'Ś'..='š' | 'ſ' => "s",
            'ß' => "ss",
            'Ţ'..='ŧ' => "t",
            'Þ' | 'þ' => "th",
            'Ù'..='Ü' | 'ù'..='ü' | 'Ũ'..='ų' => "u",
            'Ŵ' | 'ŵ' => "w",
            'Ý' | 'ý' | 'ÿ' | 'Ŷ'..='Ÿ' => "y",
            'Ź'..='ž' => "z",
            _ => return None,
        })
    }
}
