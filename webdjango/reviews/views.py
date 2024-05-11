from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Review,Wine ,Cluster
from django.contrib.auth.models import User
from .forms import ReviewForm
from .suggestions import update_clusters
import datetime
from django.contrib.auth.decorators import login_required



def review_list(request):
    latest_review_list = Review.objects.order_by('-pub_date')[:9]
    context = {'latest_review_list':latest_review_list}
    return render(request, 'review_list.html', context)


def review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request, 'review_detail.html', {'review': review})


def wine_list(request):
    wine_list = Wine.objects.order_by('-name')
    context = {'wine_list':wine_list}
    return render(request, 'wine_list.html', context)


def wine_detail(request, wine_id):
    wine = get_object_or_404(Wine, pk=wine_id)
    form = ReviewForm()
    return render(request, 'wine_detail.html', {'wine': wine, 'form': form})

@login_required
def add_review(request, wine_id):
    wine = get_object_or_404(Wine, pk=wine_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        #rating = form.cleaned_data['rating']
        #comment = form.cleaned_data['comment']
        #user_name = request.user.username
        review = Review()
        review.wine = wine
        review.user_name = request.user.username
        review.rating = form.cleaned_data['rating']
        review.comment = form.cleaned_data['comment']
        review.pub_date = datetime.datetime.now()
        review.save()
        update_clusters()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:wine_detail', args=(wine.id,)))

    return render(request, 'wine_detail.html', {'wine': wine, 'form': form})


def user_review_list(request, username=None):
    if not username:
        username = request.user.username
    latest_review_list = Review.objects.filter(user_name=username).order_by('-pub_date')
    context = {'latest_review_list':latest_review_list, 'username':username}
    return render(request, 'user_review_list.html', context)


@login_required
def user_recommendation_list(request):

    # get request user reviewed wines
    user_reviews = Review.objects.filter(user_name=request.user.username).prefetch_related('wine')
    user_reviews_wine_ids = set(map(lambda x: x.wine.id, user_reviews))

    # get request user cluster name (just the first one righ now)
    try:
        user_cluster_name = \
            User.objects.get(username=request.user.username).cluster_set.first().name
    except: # if no cluster assigned for a user, update clusters
        update_clusters()
        user_cluster_name = \
            User.objects.get(username=request.user.username).cluster_set.first().name

    # get usernames for other memebers of the cluster
    user_cluster_other_members = \
        Cluster.objects.get(name=user_cluster_name).users \
            .exclude(username=request.user.username).all()
    other_members_usernames = set(map(lambda x: x.username, user_cluster_other_members))

    # get reviews by those users, excluding wines reviewed by the request user
    other_users_reviews = \
        Review.objects.filter(user_name__in=other_members_usernames) \
            .exclude(wine__id__in=user_reviews_wine_ids)
    other_users_reviews_wine_ids = set(map(lambda x: x.wine.id, other_users_reviews))

    # then get a wine list including the previous IDs, order by rating
    wine_list = sorted(
        list(Wine.objects.filter(id__in=other_users_reviews_wine_ids)),
        key=lambda x: x.average_rating(),
        reverse=True
    )

    return render(
        request,
        'user_recommendation_list.html',
        {'username': request.user.username,'wine_list': wine_list}
)

'''
def toggle_mode(self):
    if self.actionMode.isChecked():  # Nếu đang ở chế độ tối
        self.setStyleSheet("background-color: #222; color: #FFF;")
    else:  # Nếu đang ở chế độ sáng
        self.setStyleSheet("")  # Đặt lại stylesheet về mặc định

def fontColor(self):
    color = QtWidgets.QColorDialog.getColor(self.currentFontColor)
    if color.isValid():
        self.currentFontColor = color
        self.textEdit.setTextColor(color)

def highlight(self):
    color = QtWidgets.QColorDialog.getColor(self.currentHighlightColor)
    if color.isValid():
        self.currentHighlightColor = color
        self.textEdit.setTextBackgroundColor(color)

def search_text(self):
		search_text, ok = QtWidgets.QInputDialog.getText(self.centralwidget, 'Search Text', 'Enter text to search:')
		if ok and search_text:
			cursor = self.textEdit.textCursor()
			cursor.movePosition(QtGui.QTextCursor.Start)
			cursor = self.textEdit.document().find(search_text, cursor)
			if not cursor.isNull():
				self.textEdit.setTextCursor(cursor)
				self.textEdit.ensureCursorVisible()
def toggle_mode(self):
    if self.mode == 'light':
        self.mode = 'dark'
        self.set_dark_mode()
    else:
        self.mode = 'light'
        self.set_light_mode()

def set_dark_mode(self):
    self.centralwidget.setStyleSheet("background-color: #333; color: #FFF;")
    self.textEdit.setStyleSheet("background-color: #333; color: #FFF;")
    self.menubar.setStyleSheet("background-color: #666; color: #FFF;")  # Đảo màu nền và màu chữ
    self.statusbar.setStyleSheet("background-color: #333; color: #FFF;")
    self.toolBar.setStyleSheet("background-color: #666; color: #FFF;")
    for action in self.toolBar.actions():
        action.setStyleSheet("color: #FFF;")



def set_light_mode(self):
    self.centralwidget.setStyleSheet("")
    self.textEdit.setStyleSheet("")
    self.menubar.setStyleSheet("")
    self.statusbar.setStyleSheet("")
    self.toolBar.setStyleSheet("")
    for action in self.toolBar.actions():
        action.setStyleSheet("")

def audio_to_text(self):
    # Mở cửa sổ để chọn file âm thanh
    filename, _ = QFileDialog.getOpenFileName(None, "Select Audio File", "", "Audio Files (*.wav *.mp3)")

    if filename == "":
        return

    try:
        # Chuyển đổi file mp3 thành WAV để nhận dạng âm thanh
        sound = AudioSegment.from_mp3(filename)
        filename_wav = filename[:-4] + ".wav"
        sound.export(filename_wav, format="wav")

        # Sử dụng thư viện SpeechRecognition để nhận dạng âm thanh
        recognizer = sr.Recognizer()
        with sr.AudioFile(filename_wav) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        # Thêm văn bản nhận dạng được vào cuối textEdit
        self.textEdit.moveCursor(QtGui.QTextCursor.End)
        self.textEdit.insertPlainText(text)

    except Exception as e:
        # Nếu có lỗi, thông báo cho người dùng
        QMessageBox.warning(None, "Error", str(e))

def start_spell_check_timer(self):
    if self.spell_check_checked:
        self.spell_check_timer.start(1000) 
def stop_spell_check_timer(self):
    self.spell_check_timer.stop() 

def check_spelling(self):
    self.spell_check_timer.stop()  # Dừng bộ đếm thời gian
    cursor = self.textEdit.textCursor()
    cursor_pos = cursor.position()  # Lưu lại vị trí của con trỏ

    # Lấy văn bản trong textEdit
    text = self.textEdit.toPlainText()

    # Tạo một danh sách để lưu trữ màu chữ của từng phần văn bản
    char_formats = []

    # Tách văn bản thành các từ và kiểm tra chính tả
    for start_pos, end_pos, word in self.iterate_words(text):
        if not self.spell_checker.check(word):
            # Nếu từ không đúng chính tả, lưu màu chữ hiện tại và áp dụng gạch chân nhiễu
            cursor.setPosition(start_pos)
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, end_pos - start_pos)
            char_format = cursor.charFormat()
            char_formats.append((start_pos, char_format.foreground()))  # Lưu trữ màu chữ hiện tại
            char_format.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)
            char_format.setUnderlineColor(Qt.red)  # Đặt màu gạch chân nhiễu là màu đỏ
            cursor.setCharFormat(char_format)
        else:
            char_formats.append(None)  # Không áp dụng gạch chân nhiễu, để màu chữ không thay đổi

    # Khôi phục màu chữ ban đầu cho các từ không cần áp dụng gạch chân nhiễu
    for i, char_format in enumerate(char_formats):
        if char_format is None:
            continue
        start_pos, color = char_format
        cursor.setPosition(start_pos)
        cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, 1)
        char_format = cursor.charFormat()
        char_format.setForeground(color)  # Thiết lập màu chữ trở lại
        cursor.setCharFormat(char_format)

    # Khôi phục vị trí của con trỏ
    cursor.setPosition(cursor_pos)



def iterate_words(self, text):
    """
    Hàm này tách văn bản thành các từ và trả về vị trí bắt đầu và kết thúc của từ trong văn bản cùng với từ đó.
    """
    in_word = False
    start_pos = 0
    for pos, char in enumerate(text):
        if char.isalnum():
            if not in_word:
                start_pos = pos
                in_word = True
        else:
            if in_word:
                yield start_pos, pos, text[start_pos:pos]
                in_word = False
    if in_word:
        yield start_pos, len(text), text[start_pos:]
'''