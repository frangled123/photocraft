//! User-facing names for the independent forks. Internal command ids and file formats stay stable.
use std::borrow::Cow;

pub const APP_NAME: &str = "Iride";

/// Apply branding after translation, without altering translation keys or user document names.
pub fn text(value: &str) -> Cow<'_, str> {
    if !["PdfCraft", "PhotoCraft", "VectorCraft"].iter().any(|name| value.contains(name)) {
        return Cow::Borrowed(value);
    }
    Cow::Owned(value.replace("PdfCraft", "Aevum").replace("PhotoCraft", "Iride").replace("VectorCraft", "Nodus"))
}

/// Localized wording owned by this fork, separate from upstream translation keys.
/// English is the fallback; existing app translations continue through `i18n`.
pub fn fork_label(source: &str) -> &str {
    fork_label_in(crate::i18n::current().code(), source)
}

fn fork_label_in<'a>(locale: &str, source: &'a str) -> &'a str {
    match (locale, source) {
        ("zh-hans", "Independent macOS ARM build") => "独立维护的 macOS ARM 版本",
        ("zh-hant", "Independent macOS ARM build") => "獨立維護的 macOS ARM 版本",
        ("zh-hans", "Independent macOS ARM fork") => "独立维护的 macOS ARM 分支",
        ("zh-hant", "Independent macOS ARM fork") => "獨立維護的 macOS ARM 分支",
        ("zh-hans", "Fork source and upstream project resources.") => "本分支源代码与上游项目资源。",
        ("zh-hant", "Fork source and upstream project resources.") => "本分支原始碼與上游專案資源。",
        ("zh-hans", "Upstream community") => "上游社区（Discord）",
        ("zh-hant", "Upstream community") => "上游社群（Discord）",
        ("zh-hans", "Upstream website") => "上游网站",
        ("zh-hant", "Upstream website") => "上游網站",
        ("zh-hans", "Upstream ArtCraft website") => "上游 ArtCraft 网站",
        ("zh-hant", "Upstream ArtCraft website") => "上游 ArtCraft 網站",
        ("zh-hans", "Independent ribbon suite") => "色带系列标志",
        ("zh-hant", "Independent ribbon suite") => "色帶系列標誌",
        ("zh-hans", "Upstream PhotoCraft website") => "上游 PhotoCraft 网站",
        ("zh-hant", "Upstream PhotoCraft website") => "上游 PhotoCraft 網站",
        ("zh-hans", "Iride source code") => "Iride 源代码",
        ("zh-hant", "Iride source code") => "Iride 原始碼",
        _ => source,
    }
}

/// Link labels identify the fork and the upstream destination without changing command ids.
pub fn link_text(command: &str) -> Option<&'static str> {
    let source = match command {
        "help.discord" => "Upstream community",
        "help.github" => "Iride source code",
        "help.website" => "Upstream PhotoCraft website",
        "help.artcraftWebsite" => "Upstream ArtCraft website",
        _ => return None,
    };
    Some(fork_label(source))
}

/// Rebrand owned commands without altering document names, presets or file-format labels.
pub fn menu_text<'a>(command: &str, value: &'a str) -> Cow<'a, str> {
    if let Some(label) = link_text(command) {
        Cow::Borrowed(label)
    } else if command == "help.about" {
        text(value)
    } else {
        Cow::Borrowed(value)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn chinese_native_menu_templates_are_translated() {
        for code in ["zh-hans", "zh-hant"] {
            let Some(lang) = crate::i18n::Lang::from_code(code) else {
                assert_ne!(option_env!("CRAFT_I18N_REQUIRED"), Some("1"), "release catalog missing: {code}");
                continue;
            };
            for source in ["About {app}", "Hide {app}", "Quit {app}", "Settings", "Services", "Hide Others", "Show All"] {
                let label = crate::i18n::tr(lang, source);
                assert_ne!(label, source, "{code}: {source}");
                assert_eq!(label.contains("{app}"), source.contains("{app}"));
            }
        }
    }

    #[test]
    fn fork_labels_localize_without_renaming_upstream_or_user_content() {
        for (code, suffix) in [("zh-hans", "源代码"), ("zh-hant", "原始碼")] {
            let source = format!("{APP_NAME} source code");
            assert!(fork_label_in(code, &source).ends_with(suffix));
            assert!(fork_label_in(code, "Upstream ArtCraft website").contains("ArtCraft"));
            assert!(!fork_label_in(code, "Independent macOS ARM build").starts_with("Independent"));
        }
        assert_eq!(fork_label_in("fr", "Unknown text"), "Unknown text");
        assert_eq!(menu_text("file.openRecent", "PhotoCraft draft.pdf"), "PhotoCraft draft.pdf");
        assert_eq!(menu_text("presets.choose", "PhotoCraft Defaults"), "PhotoCraft Defaults");
    }

    #[test]
    fn product_names_change_after_translation_but_normal_text_stays_borrowed() {
        assert_eq!(text("关于 PhotoCraft"), "关于 Iride");
        assert_eq!(text("About PdfCraft / VectorCraft"), "About Aevum / Nodus");
        assert!(matches!(text("Open…"), Cow::Borrowed(_)));
    }
}

#[cfg(test)]
mod fork_catalog_tests {
    #[test]
    fn committed_chinese_rows_are_present_in_the_embedded_catalogs() {
        for (code, catalog) in [("zh-hans", include_str!("i18n/fork/zh-hans.tsv")), ("zh-hant", include_str!("i18n/fork/zh-hant.tsv"))] {
            let Some(lang) = crate::i18n::Lang::from_code(code) else {
                assert_ne!(option_env!("CRAFT_I18N_REQUIRED"), Some("1"), "release catalog missing: {code}");
                continue;
            };
            for row in catalog.lines().filter(|row| !row.is_empty() && !row.starts_with('#')) {
                let fields: Vec<_> = row.split('\t').collect();
                assert_eq!(fields.len(), 3);
                let source = fields[1].replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\");
                let translated = fields[2].replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\");
                if fields[0] == "@plural" {
                    let (one, other) = source.split_once('|').unwrap();
                    for n in [0, 1, 2, 100] {
                        assert_eq!(crate::i18n::trn(lang, n, one, other), translated.replace("{n}", &n.to_string()), "{code}: {source}");
                    }
                } else {
                    assert_eq!(crate::i18n::tr(lang, &source), translated, "{code}: {source}");
                }
            }
        }
    }
}

#[cfg(all(test, not(target_arch = "wasm32")))]
mod fork_release_tests {
    #[test]
    fn updates_use_the_fork_and_accept_the_packaged_artifact_stem() {
        let app = crate::UPDATE_APP;
        assert_eq!(app.repo, "frangled123/photocraft");
        assert_eq!(app.name, "Iride");
        assert!(app.stems().any(|stem| stem == "iride"));
        assert_eq!(app.bundle_id(), "ai.storyteller.photocraft");
    }

    #[test]
    fn macos_declares_every_registered_interface_language() {
        let plist = include_str!("../../../packaging/macos/Info.plist.in").to_lowercase();
        for language in &crate::i18n::LANGUAGES {
            assert!(plist.contains(&format!("<string>{}</string>", language.code)), "{}", language.code);
        }
    }
}
