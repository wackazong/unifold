//! Checks the port `transliteration`: the table, and that it works as a plug-in.

use slugline_core::{slugify_with, Options, Transliterate};
use slugline_unicode::Latin;

fn slug(input: &str) -> String {
    slugify_with(input, &Options::default(), &Latin)
}

#[test]
fn diacritics_are_removed() {
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
