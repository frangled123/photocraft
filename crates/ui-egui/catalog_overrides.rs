//! Merge committed fork translations over the pinned upstream app catalog at build time.
//! The external checkout stays unchanged, so release inputs remain reproducible.
use std::collections::BTreeMap;

pub fn merge(base: &str, overrides: &str) -> Result<String, String> {
    let mut replacements = BTreeMap::new();
    for (index, line) in overrides.lines().enumerate() {
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let fields: Vec<&str> = line.split('\t').collect();
        let [context, source, translated] = fields.as_slice() else {
            return Err(format!("override row {} must have three tab-separated columns", index + 1));
        };
        if source.is_empty() || translated.is_empty() {
            return Err(format!("override row {} has an empty source or translation", index + 1));
        }
        if source.ends_with('…') != translated.ends_with('…') {
            return Err(format!("override row {} changes the trailing ellipsis", index + 1));
        }
        let sources: Vec<_> = if *context == "@plural" { source.split('|').collect() } else { vec![*source] };
        let translations: Vec<_> = if *context == "@plural" { translated.split('|').collect() } else { vec![*translated] };
        for source in sources {
            for translated in &translations {
                if placeholders(source)? != placeholders(translated)? {
                    return Err(format!("override row {} changes the placeholders", index + 1));
                }
            }
        }
        if replacements.insert((*context, *source), line).is_some() {
            return Err(format!("duplicate override at row {}", index + 1));
        }
    }
    let mut result = String::new();
    for line in base.lines() {
        if line == "# Committed independent-fork translations take precedence." {
            continue;
        }
        let mut fields = line.split('\t');
        let key = (fields.next().unwrap_or_default(), fields.next().unwrap_or_default());
        if !replacements.contains_key(&key) {
            result.push_str(line);
            result.push('\n');
        }
    }
    result.push_str("# Committed independent-fork translations take precedence.\n");
    for line in replacements.values() {
        result.push_str(line);
        result.push('\n');
    }
    Ok(result)
}

fn placeholders(value: &str) -> Result<Vec<&str>, String> {
    let mut result = Vec::new();
    let mut rest = value;
    while let Some((before, after)) = rest.split_once('{') {
        if before.contains('}') {
            return Err("unmatched closing placeholder brace".into());
        }
        let Some((name, after)) = after.split_once('}') else {
            return Err("unclosed placeholder".into());
        };
        if name.contains('{') {
            return Err("invalid placeholder".into());
        }
        result.push(name);
        rest = after;
    }
    if rest.contains('}') {
        return Err("unmatched closing placeholder brace".into());
    }
    result.sort_unstable();
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::merge;

    #[test]
    fn override_replaces_only_its_own_key_and_keeps_other_contexts_and_rows() {
        let original = "# upstream\n\tSearch…\tSearch…\nmenu\tSearch…\t菜单搜索…\n\tOpen\t打开\n";
        let merged = merge(original, "\tSearch…\t搜索…\n\tHello {name}\t你好 {name}\n").unwrap();
        assert!(!merged.contains("\tSearch…\tSearch…"));
        assert!(merged.contains("menu\tSearch…\t菜单搜索…\n"));
        assert!(merged.contains("\tOpen\t打开\n"));
        assert!(merged.contains("\tSearch…\t搜索…\n"));
        assert!(merged.contains("\tHello {name}\t你好 {name}\n"));
        assert_eq!(merged, merge(&merged, "\tSearch…\t搜索…\n\tHello {name}\t你好 {name}\n").unwrap());
    }

    #[test]
    fn malformed_overrides_fail_instead_of_silently_shipping_english() {
        for text in ["x\ty", "\tOpen\t打开\n\tOpen\t開啟", "\tOpen…\t打开", "\tPage {n}\t页", "\tPage {n}\t页 {m}", "\tOpen\t打开 {", "\tOpen\t"] {
            assert!(merge("", text).is_err(), "{text}");
        }
    }
}

#[cfg(test)]
mod plural_tests {
    #[test]
    fn chinese_single_plural_form_preserves_each_english_forms_parameters() {
        assert!(super::merge("", "@plural\t{n} file|{n} files\t{n} 个文件\n").is_ok());
        assert!(super::merge("", "@plural\t{n} file|{n} files\t文件\n").is_err());
        assert!(super::merge("", "\t{} and {}\t{} 与 {}\n").is_ok());
        assert!(super::merge("", "\t{} and {}\t{}\n").is_err());
    }
}
