import flet as ft
import translators as ts
import ScriptVocab as sv

SUPPORTED_INPUT_LANGS = ["auto", "en", "es",
                         "fr", "de", "it", "pt", "ru", "zh"]
SUPPORTED_TARGET_LANGS = ["en", "es",
                          "fr", "de", "it", "pt", "ru", "zh"]
DEFAULT_TRANSLATOR = "bing"
DEFAULT_INPUT_LANG = "auto"
DEFAULT_TARGET_LANG = "en"
BORDER_RADIUS = 9


class VocabScriptGUI:

    def __init__(self, page: ft.Page):
        self.page = page
        self.form_data: dict[str, any] = {}

    def change_value(self, var, val):
        self.form_data[var] = val

    def submit(self, vars: list[str]):
        for var in vars:
            print(self.form_data[var], end=", ")
        print(self.form_data["filenames"])
        all_words = sv.process_files(
            'utf-8', 1, self.form_data["filenames"])
        print(f"Found {len(all_words)} words in total.")
        words_dict = sv.create_dictionary(all_words, 4)
        print(
            f"Found {len(words_dict)} unique words appearing at least {4} times.")

        # Translate the words
        translated_dict = sv.translate_dictionary(
            words_dict, self.form_data["input_lang"], self.form_data["target_lang"])

        # Write the results to a file
        with open("outpur.txt", 'w') as f:
            f.write("Count, Word, Translation\n")
            for word in words_dict:
                count = str(words_dict[word])
                translation: str = translated_dict.get(word, '')
                f.write(f"{count}, {word}, {translation}\n")
        self.page.update()

    def custom_button(self, text: str, on_click_function: callable) -> ft.ElevatedButton:
        return ft.ElevatedButton(text, style=ft.ButtonStyle(
            shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=BORDER_RADIUS), }, ), on_click=on_click_function)

    def create_dropdown(self, options: list[str], label: str, default: str, var: str) -> ft.Dropdown:
        self.form_data[var] = default
        def callback_fn(e): return self.change_value(var, e.control.value)
        return ft.Dropdown(
            width=self.page.window_width//4,
            border_radius=BORDER_RADIUS,
            options=[ft.dropdown.Option(string) for string in options],
            value=default,
            label=label,
            on_change=callback_fn
        )

def main(page: ft.Page):
    gui = VocabScriptGUI(page)
    gui.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    gui.page.vertical_alignment = ft.MainAxisAlignment.CENTER
    gui.page.title = "Script Vocab"
    gui.page.add(
        ft.Text("Script Vocab", style=ft.TextThemeStyle.DISPLAY_LARGE))

    def on_dialog_result(e: ft.FilePickerResultEvent):
        selected_file.value = f'You selected: {e.files[0].name}'
        gui.form_data["filenames"] = [file.path for file in e.files]
        gui.page.update()

    selected_file = ft.Text()
    file_picker = ft.FilePicker(on_result=on_dialog_result)
    gui.page.overlay.append(file_picker)
    file_picker_btn = gui.custom_button(
        "Select input file", on_click_function=lambda _: file_picker.pick_files(allow_multiple=True))
    
    translators = gui.create_dropdown(
        ts.translators_pool, "Translator", DEFAULT_TRANSLATOR, "translator")
    input_langs = gui.create_dropdown(
        SUPPORTED_INPUT_LANGS, "Input language", DEFAULT_INPUT_LANG, "input_lang")
    target_langs = gui.create_dropdown(
        SUPPORTED_TARGET_LANGS, "Target language", DEFAULT_TARGET_LANG, "target_lang")
    dropdowns_row = ft.Row(spacing=15, alignment=ft.MainAxisAlignment.CENTER, controls=[translators, input_langs,
                                                                                        target_langs])
    
    submit_btn = gui.custom_button("Submit", on_click_function=lambda _: gui.submit(
        ["translator", "input_lang", "target_lang"]))

    gui.page.add(file_picker_btn, selected_file, dropdowns_row, submit_btn)


ft.app(target=main)
