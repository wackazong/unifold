//! Checks the guarantees of the port `plugin-api` (see ../README.md).

use slugline_core::{slugify_with, Options, Transliterate};

/// A plug-in that knows three characters.
struct Sample;

impl Transliterate for Sample {
    fn transliterate(&self, c: char) -> Option<&str> {
        match c {
            'ß' => Some("ss"),
            'É' => Some("E"),
            '→' => Some(" to "),
            '™' => Some(""),
            _ => None,
        }
    }
}

fn with_sample(input: &str) -> String {
    slugify_with(input, &Options::default(), &Sample)
}

#[test]
fn a_replacement_may_be_longer_than_one_letter() {
    assert_eq!(with_sample("Straße"), "strasse");
}

#[test]
fn a_replacement_is_treated_like_typed_text() {
    assert_eq!(with_sample("École"), "ecole"); // lower case
    assert_eq!(with_sample("A→B"), "a-to-b"); // a space in it ends a word
    assert_eq!(with_sample("Slug™"), "slug"); // empty: the character is dropped
}

#[test]
fn a_character_the_plugin_does_not_know_is_dropped() {
    assert_eq!(with_sample("naïve"), "nave");
}

#[test]
fn ascii_is_never_given_to_the_plugin() {
    struct Panics;
    impl Transliterate for Panics {
        fn transliterate(&self, c: char) -> Option<&str> {
            assert!(!c.is_ascii(), "asked for {c:?}");
            None
        }
    }
    assert_eq!(
        slugify_with("Hello, World!", &Options::default(), &Panics),
        "hello-world"
    );
}
