//! Checks the guarantees of the port `slugify` (see ../README.md).

use slugline_core::{slugify, Options};

fn default(input: &str) -> String {
    slugify(input, &Options::default())
}

#[test]
fn words_are_joined_by_one_separator() {
    assert_eq!(default("Hello, World!"), "hello-world");
    assert_eq!(default("  a  --  b__c  "), "a-b-c");
}

#[test]
fn only_lower_case_letters_digits_and_the_separator_remain() {
    let slug = default("Rust 2021: What's New? (Part #2) ~ ÄÖÜ €");
    assert_eq!(slug, "rust-2021-whats-new-part-2");
    assert!(slug
        .chars()
        .all(|c| matches!(c, 'a'..='z' | '0'..='9' | '-')));
}

#[test]
fn never_starts_or_ends_with_the_separator() {
    assert_eq!(default("--hello--"), "hello");
    assert_eq!(default("!?"), "");
    assert_eq!(default(""), "");
}

#[test]
fn characters_outside_ascii_are_dropped_without_a_plugin() {
    assert_eq!(default("Crème brûlée"), "crme-brle");
    assert_eq!(default("a\u{00a0}b"), "a-b"); // a no-break space still ends a word
}

#[test]
fn the_separator_can_be_chosen() {
    let options = Options {
        separator: '_',
        ..Options::default()
    };
    assert_eq!(slugify("Hello, World!", &options), "hello_world");
}

#[test]
fn the_slug_is_at_most_max_len_long() {
    let limit = |max| Options {
        max_len: Some(max),
        ..Options::default()
    };
    assert_eq!(slugify("hello world", &limit(8)), "hello-wo");
    assert_eq!(slugify("hello world", &limit(6)), "hello"); // no separator at the end
    assert_eq!(slugify("hello world", &limit(0)), "");
    assert_eq!(slugify("hello", &limit(99)), "hello");
}

#[test]
fn a_slug_is_its_own_slug() {
    for input in ["Hello, World!", "a  b", "x"] {
        let once = default(input);
        assert_eq!(default(&once), once);
    }
}
