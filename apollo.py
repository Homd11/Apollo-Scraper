import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import csv

# إعدادات المسار
current_folder = os.path.dirname(os.path.abspath(__file__))
profile_path = os.path.join(current_folder, "selenium_apollo_profile")
csv_file = os.path.join(current_folder, 'apollo_leads_fixed.csv')

options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={profile_path}")
options.add_argument("--no-first-run")

print("🚀 Launching Smart Scraper V2...")
driver = uc.Chrome(options=options, use_subprocess=True, version_main=143)
driver.maximize_window()

try:
    driver.get("https://app.apollo.io/#/people")
    
    print("\n" + "="*50)
    print("🛑 WAITING FOR YOU:")
    print("1. Apply your filters manually.")
    print("2. Wait until you see the names (Bill G, etc).")
    print("3. Press ENTER here.")
    print("="*50 + "\n")
    
    input("👉 Press Enter when list is ready...")

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Title', 'Company', 'Location'])

        for page in range(1, 4):
            print(f"\n--- Scraping Page {page} ---")
            
            # 1. التعديل الأول: البحث عن role='row' بدل tr
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='row']"))
                )
            except:
                print("⚠️ Still can't find rows! Are you sure the list is loaded?")
                break
            
            # سكرول عشان يحمل
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # 2. التعديل الثاني: هنجيب كل الصفوف (بما فيهم الهيدر)
            all_rows = driver.find_elements(By.XPATH, "//div[@role='row']")
            print(f"Found {len(all_rows)} row-like elements.")

            saved_count = 0
            for row in all_rows:
                try:
                    # 3. التعديل الثالث: استخراج الداتا من جوه الـ Divs
                    # الاسم غالباً بيكون Link أو Text واضح
                    try:
                        # بندور على أي رابط جوه الصف (لأن الاسم هو الرابط الوحيد غالباً)
                        name_el = row.find_element(By.XPATH, ".//a[contains(@href, '#') or contains(@class, 'Text')]")
                        name = name_el.text.strip()
                    except:
                        continue # ده غالباً صف الهيدر (Header) فوتُه
                    
                    if not name: continue # لو الاسم فاضي فوتُه

                    # الوظيفة والشركة (محاولة تخمين مكانهم)
                    # بنجيب كل الكلام اللي في الصف ونقسمه
                    row_text = row.text.split('\n')
                    
                    # دي طريقة "عمياء" بس فعالة: بناخد أول سطر اسم، وتاني سطر وظيفة
                    # (ممكن تحتاج تظبيط حسب شكل الجدول عندك)
                    title = "N/A"
                    company = "N/A"
                    location = "N/A"
                    
                    if len(row_text) > 1: title = row_text[1]
                    if len(row_text) > 2: company = row_text[2]

                    print(f"✅ Found: {name}")
                    writer.writerow([name, title, company, location])
                    saved_count += 1
                    
                except Exception as e:
                    continue

            print(f"Saved {saved_count} leads from this page.")

            # 4. زرار Next (تعديل الـ Selector)
            try:
                # بندور على أي زرار فيه سهم يمين أو كلمة Next
                next_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'ext')]")
                if next_btn.is_enabled():
                    driver.execute_script("arguments[0].click();", next_btn)
                    print("➡️ Next Page...")
                    time.sleep(6)
                else:
                    print("🏁 Last Page.")
                    break
            except:
                print("❌ Next button not found.")
                break

except Exception as e:
    print("Error:", e)

print(f"\n🎉 Done! Saved to: {csv_file}")
input("Press Enter to close...")