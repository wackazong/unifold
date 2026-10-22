//! Runs the built command and checks the port `slugline-command`.

use std::io::Write;
use std::process::{Command, Output, Stdio};

fn slugline(args: &[&str], input: &str) -> Output {
    let mut child = Command::new(env!("CARGO_BIN_EXE_slugline"))
        .args(args)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("the command starts");
    child
        .stdin
        .take()
        .unwrap()
        .write_all(input.as_bytes())
        .unwrap();
    child.wait_with_output().unwrap()
}

fn stdout(args: &[&str], input: &str) -> String {
    let output = slugline(args, input);
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).unwrap()
}

#[test]
fn arguments_become_one_slug() {
    assert_eq!(stdout(&["Hello,", "World!"], ""), "hello-world\n");
}

#[test]
fn each_line_of_standard_input_becomes_one_slug() {
    assert_eq!(
        stdout(&[], "First Post\n\nCrème brûlée\n"),
        "first-post\n\ncreme-brulee\n"
    );
}

#[test]
fn letters_with_diacritics_are_replaced_unless_ascii_is_asked_for() {
    assert_eq!(stdout(&["Zürich"], ""), "zurich\n");
    assert_eq!(stdout(&["--ascii", "Zürich"], ""), "zrich\n");
}

#[test]
fn separator_and_length_can_be_set() {
    assert_eq!(
        stdout(&["-s", "_", "-m", "7", "Hello, World!"], ""),
        "hello_w\n"
    );
    assert_eq!(stdout(&["--", "--not an option--"], ""), "not-an-option\n");
}

#[test]
fn wrong_usage_exits_with_2_and_explains() {
    for args in [
        &["--frobnicate"][..],
        &["-s", "ab"],
        &["-s", "x"],
        &["-m", "many"],
        &["-m"],
    ] {
        let output = slugline(args, "");
        assert_eq!(output.status.code(), Some(2), "{args:?}");
        assert!(output.stdout.is_empty());
        assert!(String::from_utf8_lossy(&output.stderr).contains("Usage: slugline"));
    }
}

#[test]
fn help_goes_to_standard_output() {
    assert!(stdout(&["--help"], "").starts_with("Usage: slugline"));
}
