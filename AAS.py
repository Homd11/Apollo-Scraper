import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import csv

# 1. إعداد المسار والبروفايل (نفس القديم بالظبط)
current_folder = os.path.dirname(os.path.abspath(__file__))
profile_path = os.path.join(current_folder, "selenium_apollo_profile")
csv_file = os.path.join(current_folder, 'apollo_leads.csv')

options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={profile_path}")
options.add_argument("--no-first-run")

# تشغيل المتصفح
print("🚀 Launching Scraper...")
# بنستخدم version_main=143 زي ما اتفقنا عشان المشكلة القديمة
driver = uc.Chrome(options=options, use_subprocess=True, version_main=143)
driver.maximize_window()

try:
    # 2. الذهاب لصفحة "الأشخاص" مباشرة
    print("Navigating to People Search...")
    driver.get("https://app.apollo.io/#/people")
    
    # 3. فتح ملف CSV للكتابة
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Title', 'Company', 'Location']) # العناوين
        
        # هنلف مثلاً على أول 3 صفحات (للتجربة)
        for page in range(1, 4):
            print(f"\n--- Scraping Page {page} ---")
            
            # انتظار الجدول يحمل (أهم خطوة)
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//tbody/tr"))
                )
            except:
                print("Table took too long or not found!")
                break

            # هات كل الصفوف (الناس) اللي في الصفحة
            rows = driver.find_elements(By.XPATH, "//tbody/tr")
            print(f"Found {len(rows)} people on this page.")
            
            for row in rows:
                try:
                    # استخراج البيانات (Apollo HTML معقد شوية فبنستخدم Xpath ذكي)
                    
                    # الاسم: غالباً بيكون أول رابط في الصف
                    name = row.find_element(By.XPATH, ".//td[1]//a").text
                    
                    # الوظيفة: بتكون سبان جنب الاسم
                    try:
                        title = row.find_element(By.XPATH, ".//td[1]//span").text
                    except:
                        title = "N/A"
                        
                    # الشركة: غالباً في العمود التاني
                    try:
                        company = row.find_element(By.XPATH, ".//td[2]//a").text
                    except:
                        company = "N/A"
                        
                    # المكان: العمود اللي بعده
                    try:
                        location = row.find_element(By.XPATH, ".//td[4]//span").text
                    except:
                        location = "N/A"

                    print(f"👤 {name} | 💼 {company}")
                    
                    # حفظ في الملف
                    writer.writerow([name, title, company, location])
                    
                except Exception as e:
                    # لو صف فاضي أو إعلان تجاهله
                    continue
            
            # 4. الانتقال للصفحة التالية (Next Button)
            try:
                # زرار النيكست في Apollo دايما ليه شكل معين
                next_btn = driver.find_element(By.XPATH, "//button[@aria-label='Go to next page']")
                
                if next_btn.is_enabled():
                    driver.execute_script("arguments[0].click();", next_btn)
                    print("Clicked Next... Waiting for reload.")
                    time.sleep(5) # استنى التحميل
                else:
                    print("No more pages.")
                    break
            except:
                print("Next button not found.")
                break

except Exception as e:
    print("Error during scraping:", e)

print(f"\n✅ Done! Check file: {csv_file}")
# driver.quit() # سيبه مفتوح عشان تتأكد