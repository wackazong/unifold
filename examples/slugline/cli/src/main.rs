//! The command `slugline`: one slug from the arguments, or one per line of
//! standard input.

use std::io::{self, BufRead, Write};
use std::process::ExitCode;

use slugline_core::{slugify, slugify_with, Options};
use slugline_unicode::Latin;

const USAGE: &str = "\
Usage: slugline [OPTIONS] [TEXT]...

Prints TEXT as one URL slug. Without TEXT, prints one slug for each line of
standard input.

Options:
  -s, --separator CHAR  put CHAR between words (default: -)
  -m, --max-len N       cut the slug after N characters
      --ascii           drop letters with diacritics instead of replacing them
  -h, --help            print this help
";

struct Request {
    options: Options,
    ascii: bool,
    text: Vec<String>,
}

fn parse(mut args: impl Iterator<Item = String>) -> Result<Option<Request>, String> {
    let mut request = Request {
        options: Options::default(),
        ascii: false,
        text: Vec::new(),
    };
    while let Some(arg) = args.next() {
        let mut value = |name: &str| args.next().ok_or(format!("{name} needs a value"));
        match arg.as_str() {
            "-h" | "--help" => return Ok(None),
            "--ascii" => request.ascii = true,
            "-s" | "--separator" => {
                let text = value("--separator")?;
                let mut chars = text.chars();
                request.options.separator = match (chars.next(), chars.next()) {
                    (Some(c), None) if c.is_ascii_graphic() && !c.is_ascii_alphanumeric() => c,
                    _ => {
                        return Err(format!(
                            "the separator must be one ASCII symbol, not '{text}'"
                        ))
                    }
                };
            }
            "-m" | "--max-len" => {
                let text = value("--max-len")?;
                let max = text
                    .parse()
                    .map_err(|_| format!("'{text}' is not a length"))?;
                request.options.max_len = Some(max);
            }
            "--" => request.text.extend(args.by_ref()),
            option if option.starts_with('-') && option.len() > 1 => {
                return Err(format!("unknown option '{option}'"));
            }
            _ => request.text.push(arg),
        }
    }
    Ok(Some(request))
}

fn run(request: &Request) -> io::Result<()> {
    let slug = |text: &str| match request.ascii {
        true => slugify(text, &request.options),
        false => slugify_with(text, &request.options, &Latin),
    };
    let mut out = io::stdout().lock();
    if request.text.is_empty() {
        for line in io::stdin().lock().lines() {
            writeln!(out, "{}", slug(&line?))?;
        }
        Ok(())
    } else {
        writeln!(out, "{}", slug(&request.text.join(" ")))
    }
}

fn main() -> ExitCode {
    match parse(std::env::args().skip(1)) {
        Ok(None) => print!("{USAGE}"),
        Ok(Some(request)) => {
            if let Err(error) = run(&request) {
                eprintln!("slugline: {error}");
                return ExitCode::FAILURE;
            }
        }
        Err(message) => {
            eprintln!("slugline: {message}\n\n{USAGE}");
            return ExitCode::from(2);
        }
    }
    ExitCode::SUCCESS
}
