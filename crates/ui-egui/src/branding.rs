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

/// Rebrand the app's About command while preserving document, preset and upstream-link labels.
pub fn menu_text<'a>(command: &str, value: &'a str) -> Cow<'a, str> {
    if command == "help.about" { text(value) } else { Cow::Borrowed(value) }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn product_names_change_after_translation_but_normal_text_stays_borrowed() {
        assert_eq!(text("关于 PhotoCraft"), "关于 Iride");
        assert_eq!(text("About PdfCraft / VectorCraft"), "About Aevum / Nodus");
        assert!(matches!(text("Open…"), Cow::Borrowed(_)));
    }
}
