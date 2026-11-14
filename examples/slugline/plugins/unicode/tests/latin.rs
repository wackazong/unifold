//! Checks the contracts `plugin-api` and `transliteration` (see ../../../docs/references/):
//! the table, and that it works as a plug-in. The first test names the ids of
//! the examples it proves, `plugin-api#transliterate/<case>`.

use slugline_core::{slugify_with, Options, Transliterate};
use slugline_unicode::Latin;

fn slug(input: &str) -> String {
    slugify_with(input, &Options::default(), &Latin)
}

#[test]
fn the_examples_of_the_contract() {
    // plugin-api#transliterate/acute-accent
    assert_eq!(Latin.transliterate('é'), Some("e"));
    // plugin-api#transliterate/stroke-upper-case
    assert_eq!(Latin.transliterate('Ø'), Some("o"));
    // plugin-api#transliterate/stroke
    assert_eq!(Latin.transliterate('ł'), Some("l"));
    // plugin-api#transliterate/ligature-upper-case
    assert_eq!(Latin.transliterate('Æ'), Some("ae"));
    // plugin-api#transliterate/sharp-s
    assert_eq!(Latin.transliterate('ß'), Some("ss"));
    // plugin-api#transliterate/an-arrow
    assert_eq!(Latin.transliterate('→'), None);
    // plugin-api#transliterate/cyrillic
    assert_eq!(Latin.transliterate('я'), None);
}

#[test]
fn diacritics_are_removed() {
    // transliteration#latin/the-plug-in
    assert_eq!(slug("Crème brûlée"), "creme-brulee");
    assert_eq!(slug("Zürich, Genève & Malmö"), "zurich-geneve-malmo");
    assert_eq!(slug("Łódź"), "lodz");
    assert_eq!(slug("ČEŠTINA"), "cestina");
}

#[test]
fn ligatures_and_special_letters_become_two_letters() {
    assert_eq!(slug("Straße"), "strasse");
    assert_eq!(slug("Œuvre"), "oeuvre");
    assert_eq!(slug("Ærø"), "aero");
    assert_eq!(slug("Þór"), "thor");
}

#[test]
fn every_answer_is_one_or_two_lower_case_ascii_letters() {
    for c in ('\u{00c0}'..='\u{017f}').filter(|c| c.is_alphabetic()) {
        let answer = Latin
            .transliterate(c)
            .unwrap_or_else(|| panic!("no answer for {c:?}"));
        assert!(matches!(answer.len(), 1 | 2), "{c:?} gives {answer:?}");
        assert!(
            answer.chars().all(|a| a.is_ascii_lowercase()),
            "{c:?} gives {answer:?}"
        );
    }
}

#[test]
fn other_scripts_and_symbols_are_not_known() {
    for c in ['я', 'λ', '漢', '€', '×', '÷'] {
        assert_eq!(Latin.transliterate(c), None);
    }
}
