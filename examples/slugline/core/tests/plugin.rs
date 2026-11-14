//! Checks the part `slugify-with` of the contract `slugify` with a sample
//! plug-in, a fake of the need `plugin-api`. Each test names the ids of the
//! examples it proves.

use slugline_core::{slugify_with, Options, Transliterate};

/// A plug-in that knows four characters: the `sample` of the examples.
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
fn every_letter_outside_ascii_is_replaced() {
    // slugify#slugify-with/letters-replaced
    struct Accents;
    impl Transliterate for Accents {
        fn transliterate(&self, c: char) -> Option<&str> {
            match c {
                'è' | 'é' => Some("e"),
                'û' => Some("u"),
                _ => None,
            }
        }
    }
    assert_eq!(
        slugify_with("Crème brûlée", &Options::default(), &Accents),
        "creme-brulee"
    );
}

#[test]
fn a_replacement_may_be_longer_than_one_letter() {
    assert_eq!(Sample.transliterate('ß'), Some("ss"));
    // slugify#slugify-with/one-letter-becomes-two
    assert_eq!(with_sample("Straße"), "strasse");
}

#[test]
fn a_replacement_is_treated_like_typed_text() {
    assert_eq!(Sample.transliterate('É'), Some("E"));
    // slugify#slugify-with/answer-in-upper-case
    assert_eq!(with_sample("École"), "ecole");
    assert_eq!(Sample.transliterate('→'), Some(" to "));
    // slugify#slugify-with/answer-with-a-space
    assert_eq!(with_sample("A→B"), "a-to-b");
    assert_eq!(Sample.transliterate('™'), Some(""));
    // slugify#slugify-with/empty-answer
    assert_eq!(with_sample("Slug™"), "slug");
}

#[test]
fn a_character_the_plugin_does_not_know_is_dropped() {
    assert_eq!(Sample.transliterate('ï'), None);
    // slugify#slugify-with/plug-in-does-not-know
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
