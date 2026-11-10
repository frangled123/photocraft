//! The fork’s ribbon app icon, cached separately for light and dark UI themes.

use egui::{Color32, Context, Id, Rect, TextureHandle, TextureOptions, Ui, pos2};
use photocraft_codecs::{ChannelLayout, SampleType};

/// 128 px: sharp at 20 pt on a 3× display, and the mipmaps keep it clean at 1×.
const ICON_PNG: &[u8] = include_bytes!("../../../../assets/app-icon/hicolor/128x128/apps/ai.storyteller.photocraft.png");
const DARK_ICON_PNG: &[u8] = include_bytes!("../../../../assets/app-icon/photocraft-dark-128.png");

/// The icon's pixels (one transparent pixel if it couldn't be decoded, which a test rules out).
fn decode(dark: bool) -> egui::ColorImage {
    let png = if dark { DARK_ICON_PNG } else { ICON_PNG };
    decode_png(png)
}

fn decode_png(png: &[u8]) -> egui::ColorImage {
    let rgba = photocraft_codecs::decode(png).ok().map(|img| img.convert(ChannelLayout::Rgba, SampleType::U8));
    match rgba {
        Some(img) if img.data().len() == img.width() as usize * img.height() as usize * 4 => {
            egui::ColorImage::from_rgba_unmultiplied([img.width() as usize, img.height() as usize], img.data())
        }
        _ => egui::ColorImage::filled([1, 1], Color32::TRANSPARENT),
    }
}

/// The icon texture, uploaded on first use and kept in the context.
fn texture(ctx: &Context) -> TextureHandle {
    let dark = ctx.global_style().visuals.dark_mode;
    let id = Id::unique("photocraft-brand-mark").with(dark);
    if let Some(tex) = ctx.data(|d| d.get_temp::<TextureHandle>(id)) {
        return tex;
    }
    let options = TextureOptions { mipmap_mode: Some(egui::TextureFilter::Linear), ..TextureOptions::LINEAR };
    let tex = ctx.load_texture("photocraft-brand-mark", decode(dark), options);
    ctx.data_mut(|d| d.insert_temp(id, tex.clone()));
    tex
}

/// Where the mark was painted this frame (tests and screenshots).
fn rect_id() -> Id {
    Id::unique("photocraft-brand-mark-rect")
}

/// Paint the mark into `r` (square).
pub fn paint_mark(ui: &Ui, r: Rect) {
    let uv = Rect::from_min_max(pos2(0.0, 0.0), pos2(1.0, 1.0));
    ui.painter().image(texture(ui.ctx()).id(), r, uv, Color32::WHITE);
    ui.ctx().data_mut(|d| d.insert_temp(rect_id(), r));
}

/// The rect the mark was last painted into.
#[cfg(test)]
pub fn mark_rect(ctx: &Context) -> Option<Rect> {
    ctx.data(|d| d.get_temp(rect_id()))
}

/// Decode the shared mark directly: these apps do not install egui's PNG ImageLoader.
fn suite_texture(ctx: &Context) -> TextureHandle {
    let dark = ctx.global_style().visuals.dark_mode;
    let id = Id::unique("fork-suite-ribbon").with(dark);
    if let Some(tex) = ctx.data(|d| d.get_temp::<TextureHandle>(id)) {
        return tex;
    }
    let png: &[u8] =
        if dark { include_bytes!("../../../../docs/brand/ribbon-mark-dark.png") } else { include_bytes!("../../../../docs/brand/ribbon-mark-light.png") };
    let tex = ctx.load_texture("fork-suite-ribbon", decode_png(png), TextureOptions::LINEAR);
    ctx.data_mut(|d| d.insert_temp(id, tex.clone()));
    tex
}

/// Show the shared ribbon without depending on optional image-loader features.
pub fn suite_mark(ui: &mut Ui, size: f32) -> egui::Response {
    let tex = suite_texture(ui.ctx());
    ui.add(
        egui::Image::new((tex.id(), tex.size_vec2()))
            .fit_to_exact_size(egui::vec2(size, size))
            .alt_text(crate::branding::fork_label("Independent ribbon suite")),
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn shared_ribbon_renders_in_both_themes_without_image_loaders() {
        let ctx = Context::default();
        let mut ids = Vec::new();
        for theme in [egui::ThemePreference::Light, egui::ThemePreference::Dark] {
            ctx.set_theme(theme);
            let texture = suite_texture(&ctx);
            assert!(texture.size()[0] > 1 && texture.size()[1] > 1);
            let out = ctx.run_ui(egui::RawInput::default(), |ui| {
                suite_mark(ui, 28.0);
            });
            // Image widgets may use a textured RectShape before tessellation. Verify the
            // actual mesh submitted to the renderer instead of an internal shape variant.
            let primitives = ctx.tessellate(out.shapes, out.pixels_per_point);
            assert!(primitives.iter().any(|shape| matches!(&shape.primitive, egui::epaint::Primitive::Mesh(mesh) if mesh.texture_id == texture.id())));
            assert_eq!(suite_texture(&ctx).id(), texture.id());
            ids.push(texture.id());
        }
        assert_ne!(ids[0], ids[1]);
    }

    #[test]
    fn theme_switch_selects_and_reuses_the_matching_texture() {
        let ctx = Context::default();
        ctx.set_visuals(egui::Visuals::light());
        let light = texture(&ctx).id();
        ctx.set_visuals(egui::Visuals::dark());
        let dark = texture(&ctx).id();
        assert_ne!(light, dark);
        assert_ne!(decode(false).pixels, decode(true).pixels);
        assert_eq!(decode(true).size, [128, 128]);
        ctx.set_visuals(egui::Visuals::light());
        assert_eq!(texture(&ctx).id(), light);
    }

    #[test]
    fn the_icon_decodes_to_a_rounded_128_px_tile() {
        let img = decode(false);
        assert_eq!(img.size, [128, 128]);
        // Rounded corners: the corner pixel is transparent, the centre opaque.
        assert_eq!(img.pixels[0].a(), 0);
        assert_eq!(img.pixels[64 * 128 + 64].a(), 255);
    }

    #[test]
    fn the_title_bar_paints_the_icon_from_one_cached_texture() {
        let ctx = Context::default();
        crate::PhotocraftApp::setup_context(&ctx, crate::theme::ThemeKind::ALL[0]);
        let mut app = crate::PhotocraftApp::new(photocraft_engine::Session::new(), crate::Services::default());
        // The system title bar hides the in-app mark (the OS draws its own icon), so paint the
        // app-drawn bar here.
        app.custom_titlebar = true;
        let mut frame = || {
            let mut out = ctx.run_ui(egui::RawInput::default(), |ui| crate::panels::title_bar(&mut app, ui));
            let uploads = out.textures_delta.set.values().flat_map(|d| d.iter()).filter(|d| d.image.size() == [128, 128]).count();
            out.textures_delta.clear();
            uploads
        };
        assert_eq!(frame(), 1, "uploaded on first use");
        assert_eq!(frame(), 0, "then reused");
        assert!(mark_rect(&ctx).is_some());
    }
}
