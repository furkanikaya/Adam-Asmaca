# -*- coding: utf-8 -*-

import json
import random
import os
import time
from game_data import STAGES, WORDS_BY_CATEGORY

# --- Sabitler ---
MAX_ERRORS = len(STAGES) - 1
SCORES_FILE = "scores.json"

# Puanlama sabitleri
SCORE_CORRECT_GUESS = 10
SCORE_WRONG_GUESS = -5
SCORE_CORRECT_MATH = 15
SCORE_WRONG_MATH = -10
SCORE_WIN = 50
SCORE_LOSE = -20

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_scores():
    """scores.json dosyasından skorları yükler."""
    try:
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_scores(scores):
    """Skorları scores.json dosyasına kaydeder."""
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f, indent=4)

def display_high_scores(scores):
    """En yüksek skorları gösterir."""
    print("\n--- En Yüksek Skorlar ---")
    if not scores:
        print("Henüz kaydedilmiş bir skor yok.")
    else:
        # Skorları puana göre büyükten küçüğe sırala
        sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        for i, record in enumerate(sorted_scores[:5]):
            print(f"{i+1}. {record['name']}: {record['score']} puan")
    print("-" * 25)

def get_word_and_category():
    """Kategorilerden rastgele bir kelime ve kategori adı seçer."""
    category = random.choice(list(WORDS_BY_CATEGORY.keys()))
    word = random.choice(WORDS_BY_CATEGORY[category])
    return word.upper(), category

def display_game_state(lives, hidden_word, guessed_letters, score, bonus_points, used_operations, category_revealed, category):
    """Oyunun mevcut durumunu ekrana basar."""
    clear_screen()
    print("=== Calc & Hang: İşlem Yap, Harfi Kurtar! ===")
    print("--- Yeni Tur ---")
    print(STAGES[MAX_ERRORS - lives])
    print("\n" + "="*30)

    print(f"Kelime: {' '.join(hidden_word)}")
    print(f"Tahmin edilen harfler: {', '.join(sorted(guessed_letters)) if guessed_letters else '-'}")
    print(f"Bonus puan: {bonus_points}")
    print(f"Toplam Puan: {score}")
    print(f"Kalan Hata Hakkı: {lives}")

    if category_revealed:
        print(f"İpucu: Kelimenin kategorisi -> {category.capitalize()}")

    print("\nSeçenekler: [H]arf tahmini | [İ]şlem çöz | [I]pucu | [Ç]ıkış")

def handle_letter_guess(chosen_word, hidden_word, guessed_letters, lives, score):
    """Harf tahminini yönetir ve oyun durumunu günceller."""
    guess = input("Bir harf tahmin edin: ").upper()

    if not guess.isalpha() or len(guess) != 1:
        print("Geçersiz giriş. Lütfen sadece bir harf girin.")
        time.sleep(1.5)
        return lives, score, False

    if guess in guessed_letters:
        print(f"'{guess}' harfini zaten tahmin ettiniz. Lütfen başka bir harf deneyin.")
        time.sleep(1.5)
        return lives, score, False

    guessed_letters.add(guess)

    if guess in chosen_word:
        print(f"Doğru tahmin! '{guess}' harfi kelimede var.")
        score += SCORE_CORRECT_GUESS
        for i, letter in enumerate(chosen_word):
            if letter == guess:
                hidden_word[i] = guess
    else:
        print(f"Yanlış tahmin! '{guess}' harfi kelimede yok.")
        lives -= 1
        score += SCORE_WRONG_GUESS

    time.sleep(1.5)

    # Oyunun bitip bitmediğini kontrol et
    if "_" not in hidden_word:
        return lives, score, True # Kazanma durumu
    if lives <= 0:
        return lives, score, True # Kaybetme durumu

    return lives, score, False

def handle_math_problem(score, bonus_points, lives, hidden_word, chosen_word, guessed_letters, used_operations):
    """Matematik problemini yönetir ve oyun durumunu günceller."""
    available_ops = [op for op in ['+', '-', '*', '/'] if op not in used_operations]
    if not available_ops:
        print("Çözülecek yeni bir işlem kalmadı!")
        time.sleep(1.5)
        return score, bonus_points, lives, False

    print(f"Kullanılabilir işlemler: {', '.join(available_ops)}")
    op = input("Çözmek istediğiniz işlemi seçin (veya 'iptal' yazın): ").strip()

    if op.lower() == 'iptal':
        return score, bonus_points, lives, False

    if op not in available_ops:
        print("Geçersiz veya daha önce kullanılmış bir işlem seçtiniz.")
        time.sleep(1.5)
        return score, bonus_points, lives, False

    try:
        num1 = float(input("İlk sayıyı girin: "))
        num2 = float(input("İkinci sayıyı girin: "))
        user_result_str = input(f"{num1} {op} {num2} = ? Sonucu girin: ")

        # Kullanıcı "iptal" derse işlemi bitir
        if user_result_str.lower() == 'iptal':
             return score, bonus_points, lives, False

        user_result = float(user_result_str)

    except ValueError:
        print("Geçersiz sayı girdiniz. İşlem iptal edildi.")
        lives -= 1
        score += SCORE_WRONG_MATH
        time.sleep(1.5)
        return score, bonus_points, lives, lives <= 0

    expected_result = 0
    correct = False

    if op == '+':
        expected_result = num1 + num2
    elif op == '-':
        expected_result = num1 - num2
    elif op == '*':
        expected_result = num1 * num2
    elif op == '/':
        if num2 == 0:
            print("Hata: Sıfıra bölme! Ceza olarak bir can kaybettiniz.")
            lives -= 1
            score += SCORE_WRONG_MATH
            time.sleep(1.5)
            return score, bonus_points, lives, lives <= 0
        expected_result = num1 / num2

    # Ondalık karşılaştırması için tolerans
    if abs(user_result - expected_result) <= 1e-6:
        correct = True

    if correct:
        print("Tebrikler! Doğru sonuç.")
        score += SCORE_CORRECT_MATH
        bonus_points += 1
        used_operations.add(op)

        # Kelimede henüz açılmamış rastgele bir harf aç
        unrevealed_indices = [i for i, char in enumerate(hidden_word) if char == "_"]
        if unrevealed_indices:
            idx_to_reveal = random.choice(unrevealed_indices)
            letter_to_reveal = chosen_word[idx_to_reveal]

            # Aynı harfin tümünü aç
            for i, letter in enumerate(chosen_word):
                if letter == letter_to_reveal:
                    hidden_word[i] = letter
                    guessed_letters.add(letter)
            print(f"Bonus olarak '{letter_to_reveal}' harfi açıldı!")

    else:
        print(f"Yanlış sonuç! Doğru cevap: {expected_result:.2f}")
        lives -= 1
        score += SCORE_WRONG_MATH

    time.sleep(2)

    if "_" not in hidden_word:
        return score, bonus_points, lives, True # Kazanma

    return score, bonus_points, lives, lives <= 0


def handle_hint(bonus_points, category_revealed, score):
    """İpucu kullanımını yönetir."""
    if category_revealed:
        print("İpucunu zaten kullandınız.")
        time.sleep(1.5)
        return bonus_points, True, score

    if bonus_points > 0:
        print("1 bonus puan harcayarak kelimenin kategorisini öğrendiniz.")
        bonus_points -= 1
        # Puanlama sistemine göre ipucu kullanımında puan düşmez, sadece bonus azalır.
        # İstenirse buraya `score -= X` eklenebilir. Proje tanımında -1 bonus diyor.
        time.sleep(1.5)
        return bonus_points, True, score
    else:
        print("İpucu almak için yeterli bonus puanınız yok. (Gereken: 1)")
        time.sleep(1.5)
        return bonus_points, False, score

def game_loop():
    """Oyunun ana döngüsü."""
    chosen_word, category = get_word_and_category()
    hidden_word = ["_"] * len(chosen_word)
    guessed_letters = set()
    used_operations = set()

    lives = MAX_ERRORS
    score = 0
    bonus_points = 0
    category_revealed = False
    game_over = False

    while not game_over:
        display_game_state(lives, hidden_word, guessed_letters, score, bonus_points, used_operations, category_revealed, category)

        choice = input("Seçiminiz: ").upper()

        if choice == 'H':
            lives, score, game_over = handle_letter_guess(chosen_word, hidden_word, guessed_letters, lives, score)
        elif choice == 'İ':
            score, bonus_points, lives, game_over = handle_math_problem(score, bonus_points, lives, hidden_word, chosen_word, guessed_letters, used_operations)
        elif choice == 'I':
            bonus_points, category_revealed, score = handle_hint(bonus_points, category_revealed, score)
        elif choice == 'Ç':
            print("\nOyundan çıkılıyor...")
            time.sleep(1)
            return # Oyunu bitir
        else:
            print("Geçersiz seçim! Lütfen tekrar deneyin.")
            time.sleep(1)
            continue

        if game_over:
            display_game_state(lives, hidden_word, guessed_letters, score, bonus_points, used_operations, category_revealed, category)
            if "_" not in hidden_word:
                print(f"\n*** Tebrikler! Kazandınız! Kelime: {chosen_word} ***")
                score += SCORE_WIN
            else:
                print(f"\n--- Kaybettiniz! Doğru kelime: {chosen_word} ---")
                score += SCORE_LOSE

            print(f"Final Puanınız: {score}")

            # Skoru kaydet
            scores = load_scores()
            player_name = input("Lütfen adınızı girin: ")
            scores.append({"name": player_name, "score": score})
            save_scores(scores)

def main():
    """Ana fonksiyon, oyunu başlatır ve tekrar oynama seçeneği sunar."""
    while True:
        game_loop()

        scores = load_scores()
        display_high_scores(scores)

        play_again = input("Tekrar oynamak ister misiniz? (E/H): ").upper()
        if play_again != 'E':
            break
    print("\nOynadığınız için teşekkürler!")

if __name__ == "__main__":
    main()
