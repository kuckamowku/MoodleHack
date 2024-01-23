import base64
import json
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QFileDialog, QMessageBox, QTextEdit, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Moodle sostb")
        self.setGeometry(100, 100, 400, 250)
        self.lbl = QLabel("Файл не выбран", self)
        self.lbl.move(10, 10)
        btn = QPushButton("Выбрать файл", self)
        btn.clicked.connect(self.choose_path)
        btn.move(150, 10)

    def home(self):
        self.lbl.setText("Файл не выбран")

    def get_answer(self, text):
        answer = []
        if len(text) == 1:
            return text[0]['t']
        for i in range(len(text)):
            try:
                answer.append((text[i]['t']['d'][0], text[i]['c']))
            except:
                answer.append((text[i]['ia']['i'], text[i]['c']))
        return answer

    def get_answers(self, filepath):
        with open(filepath, 'r', encoding='UTF-8') as file:
            text = file.read()
        text = base64.b64decode(text[text.index('var data'):].split('"')[1])
        text = text.decode(encoding='UTF-8')
        text = json.loads(text)
        questions = []
        answers = []
        for j in range(len(text['d']['sl']['g'])):
            if len(text['d']['sl']['g']) > 1 and j == 0:
                continue
            for i in range(len(text['d']['sl']['g'][j]['S'])):
                questions.append(text['d']['sl']['g'][j]['S'][i]['D']['d'][0])
                answer = 'N/A'
                try:
                    if 'm' in text['d']['sl']['g'][j]['S'][i]['C'].keys():  # Ключ для заданий типа установите соответствие
                        answer = []
                        for k in range(len(text['d']['sl']['g'][j]['S'][i]['C']['m'])):
                            answer.append([text['d']['sl']['g'][j]['S'][i]['C']['m'][k]['p']['t']['d'][0],
                                           text['d']['sl']['g'][j]['S'][i]['C']['m'][k]['r']['t']['d'][0]])
                    elif 'chs' in text['d']['sl']['g'][j]['S'][i]['C'].keys():  # Ключ для заданий TRUE/FALSE
                        answer = self.get_answer(text['d']['sl']['g'][j]['S'][i]['C']['chs'])
                    elif 'na' in text['d']['sl']['g'][j]['S'][i]['C'].keys():  # Ключ для заданий с вводом ответа
                        if 'op' in text['d']['sl']['g'][j]['S'][i]['C']['na'][0].keys():  # Ключ для заданий с вводом однозначного ответа
                            answer = text['d']['sl']['g'][j]['S'][i]['C']['na'][0]['op']
                        elif 'co' in text['d']['sl']['g'][j]['S'][i]['C']['na'][0].keys():  # Ключ для заданий с числовыми ответами в заданном промежутке
                            answer = f"Ответ - число в промежутке между {text['d']['sl']['g'][j]['S'][i]['C']['na'][0]['lo']}" \
                                     f" и {text['d']['sl']['g'][j]['S'][i]['C']['na'][0]['ro']}"
                except:
                    answer = 'N/A'
                answers.append(answer)
        return questions, answers

    def save_answers(self, path, answers, questions):
        with open(path, 'w', encoding='UTF-8') as file:
            count = 0
            for i in zip(questions, answers):
                file.write(f'Вопрос {count + 1}: {i[0]}\n')
                if isinstance(i[1], list):
                    for j in i[1]:
                        file.write(f'{j[0]} - {j[1]}\n')
                else:
                    file.write(f'{i[1]}\n')
                file.write('\n')
                count += 1

    def choose_path(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Html files (*.html)")
        if filepath:
            self.lbl.setText(filepath)
            response = QMessageBox.question(self, 'Получить ответы?', 'Выбирая вариант ответа "Да", помни: '
                                                                  'с большой силой приходит большая ответственность!',
                                           QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if response == QMessageBox.Yes:
                try:
                    questions, answers = self.get_answers(filepath)
                except:
                    QMessageBox.critical(self, 'Ошибка', '!!!Выбран некоректный файл, попробуй еще раз!!!')
                    return
                savepath, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', '', 'Text Documents (*.txt)')
                while not savepath:
                    QMessageBox.critical(self, 'Ошибка', '!!!Выбери куда сохранить ответы!!!')
                    savepath, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', '', 'Text Documents (*.txt)')
                self.save_answers(savepath, answers, questions)
                QMessageBox.information(self, 'Успех', f'Ответы успешно сохранены!\nПуть: {savepath}')
                self.home()
            elif response == QMessageBox.No:
                self.home()


if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()