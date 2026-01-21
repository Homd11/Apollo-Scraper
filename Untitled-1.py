import time
import random
import csv # 1. استيراد مكتبة ملفات الإكسل (CSV)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# إعدادات التمويه
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=chrome_options)
driver.maximize_window()

print("Opening AMAZON...")
driver.get("https://www.amazon.com/")

# ---------------------------------------------------------
# 2. فتح الملف (الخزنة اللي هنحط فيها الداتا)
# ---------------------------------------------------------
# 'w' يعني write (كتابة ملف جديد)
# newline='' عشان ميعملش سطور فاضية زيادة
# encoding='utf-8' عشان يدعم عربي وإنجليزي ورموز
file = open('amazon_products.csv', mode='w', newline='', encoding='utf-8')
writer = csv.writer(file)

# كتابة العناوين (رأس الجدول)
writer.writerow(['Rank', 'Product Name']) 

try:
    # البحث
    search_box = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
    )
    search_box.send_keys("PLAYSTATION 5")
    search_box.send_keys(Keys.RETURN)
    
    page_number = 1
    global_rank = 1 # عداد عشان يرقم المنتجات 1, 2, 3...
    
    while True:
        print(f"\n--- Scraping Page {page_number} ---")
        
        # سكرول بشري
        for i in range(1, 6):
            driver.execute_script(f"window.scrollTo(0, {i * 800});")
            time.sleep(random.uniform(0.5, 1.5))

        # سحب المنتجات
        products = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 's-result-item')]//h2//span"))
        )

        print(f"Found {len(products)} products. Writing to file...")
        
        for product in products:
            if product.text.strip() != "":
                product_name = product.text
                
                # طباعة في التيرمينال عشان نشوف الشغل
                print(f"{global_rank}. {product_name}")
                
                # -----------------------------------------------------
                # 3. الحفظ في الملف (أهم سطر)
                # -----------------------------------------------------
                writer.writerow([global_rank, product_name])
                
                global_rank += 1 # زود العداد

        # الانتقال للصفحة التالية
        try:
            print("\nLooking for 'Next' button...")
            next_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 's-pagination-next')]"))
            )
            driver.execute_script("arguments[0].click();", next_btn)
            print("Clicked Next! Moving to next page...")
            page_number += 1
            time.sleep(random.uniform(3, 6))
            
        except:
            print("No 'Next' button found or last page reached.")
            break 

except Exception as e:
    print("Error:", e)

# لازم نقفل الملف في الآخر عشان الداتا تتحفظ
file.close() 
print("File Saved Successfully: amazon_products.csv")

driver.quit()