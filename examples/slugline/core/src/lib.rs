//! Turns text into URL slugs.
//!
//! ```
//! use slugline_core::{slugify, Options};
//! assert_eq!(slugify("Hello, World!", &Options::default()), "hello-world");
//! ```

/// Maps a character outside ASCII to ASCII text. This is the plug-in interface.
///
/// An implementation has no side effects and gives the same answer for the
/// same character. The answer may be empty and may be longer than one letter.
pub trait Transliterate {
    /// The replacement for `c`, or `None` if this plug-in does not know `c`.
    fn transliterate(&self, c: char) -> Option<&str>;
}

/// How a slug is made.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Options {
    /// Stands between words. Default: `-`.
    pub separator: char,
    /// The longest slug allowed, in characters. `None`: no limit.
    pub max_len: Option<usize>,
}

impl Default for Options {
    fn default() -> Self {
        Options {
            separator: '-',
            max_len: None,
        }
    }
}

/// Makes a slug from `input`. Characters outside ASCII are dropped.
pub fn slugify(input: &str, options: &Options) -> String {
    build(input, options, None)
}

/// Makes a slug from `input`; `plugin` replaces characters outside ASCII.
pub fn slugify_with(input: &str, options: &Options, plugin: &dyn Transliterate) -> String {
    build(input, options, Some(plugin))
}

fn build(input: &str, options: &Options, plugin: Option<&dyn Transliterate>) -> String {
    let mut slug = Slug {
        text: String::new(),
        gap: false,
        separator: options.separator,
    };
    for c in input.chars() {
        if c.is_ascii() {
            slug.push_ascii(c);
        } else if let Some(replacement) = plugin.and_then(|p| p.transliterate(c)) {
            replacement.chars().for_each(|r| slug.push_ascii(r));
        } else if c.is_whitespace() {
            slug.gap = true;
        }
    }
    if let Some(max) = options.max_len {
        if let Some((cut, _)) = slug.text.char_indices().nth(max) {
            slug.text.truncate(cut);
        }
        while slug.text.ends_with(options.separator) {
            slug.text.pop();
        }
    }
    slug.text
}

/// A slug under construction. `gap` is set when a word has ended.
struct Slug {
    text: String,
    gap: bool,
    separator: char,
}

impl Slug {
    /// Letters and digits are kept in lower case, an apostrophe is dropped,
    /// anything else ends the word.
    fn push_ascii(&mut self, c: char) {
        if c.is_ascii_alphanumeric() {
            if self.gap && !self.text.is_empty() {
                self.text.push(self.separator);
            }
            self.gap = false;
            self.text.push(c.to_ascii_lowercase());
        } else if c != '\'' {
            self.gap = true;
        }
    }
}
