#!/usr/bin/env python3
"""
Test script for anti-detection features
测试反检测功能的脚本
"""

import time
from webdriver_manager import WebDriverManager

def test_anti_detection():
    """Test anti-detection features"""
    print("=" * 60)
    print("Testing Anti-Detection Features")
    print("测试反检测功能")
    print("=" * 60)
    
    driver_manager = WebDriverManager()
    driver = None
    
    try:
        print("\n[1/5] Creating WebDriver...")
        driver = driver_manager.create_driver()
        print("✓ WebDriver created successfully")
        
        print("\n[2/5] Navigating to detection test page...")
        driver.get('https://bot.sannysoft.com/')
        print("✓ Page loaded")
        
        print("\n[3/5] Waiting for page to fully load...")
        time.sleep(3)
        
        print("\n[4/5] Checking anti-detection features...")
        
        # Check webdriver property
        webdriver_value = driver.execute_script("return navigator.webdriver")
        print(f"  navigator.webdriver: {webdriver_value}")
        if webdriver_value is None or webdriver_value is False:
            print("  ✓ webdriver property is hidden")
        else:
            print("  ✗ webdriver property is exposed!")
        
        # Check platform
        platform = driver.execute_script("return navigator.platform")
        print(f"  navigator.platform: {platform}")
        if platform == 'Win32':
            print("  ✓ Platform spoofed to Windows")
        else:
            print(f"  ⚠ Platform is {platform}, not Win32")
        
        # Check user agent
        user_agent = driver.execute_script("return navigator.userAgent")
        print(f"  navigator.userAgent: {user_agent[:50]}...")
        if 'Windows NT' in user_agent and 'Chrome' in user_agent:
            print("  ✓ User-Agent spoofed to Windows Chrome")
        else:
            print("  ⚠ User-Agent may not be properly spoofed")
        
        # Check chrome object
        has_chrome = driver.execute_script("return typeof window.chrome !== 'undefined'")
        print(f"  window.chrome exists: {has_chrome}")
        if has_chrome:
            print("  ✓ Chrome object is present")
        else:
            print("  ✗ Chrome object is missing!")
        
        # Check languages
        languages = driver.execute_script("return navigator.languages")
        print(f"  navigator.languages: {languages}")
        if 'zh-CN' in languages:
            print("  ✓ Languages properly set")
        else:
            print("  ⚠ Languages may not be properly set")
        
        print("\n[5/5] Taking screenshot for visual inspection...")
        driver.save_screenshot('test_detection_result.png')
        print("✓ Screenshot saved as 'test_detection_result.png'")
        print("\n  Please check the screenshot to see if any red warnings appear.")
        print("  请检查截图，查看是否有红色警告。")
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("测试完成！")
        print("=" * 60)
        
        print("\nResults Summary:")
        print("结果摘要：")
        print(f"  - WebDriver hidden: {'✓' if not webdriver_value else '✗'}")
        print(f"  - Platform spoofed: {'✓' if platform == 'Win32' else '⚠'}")
        print(f"  - User-Agent spoofed: {'✓' if 'Windows NT' in user_agent else '⚠'}")
        print(f"  - Chrome object present: {'✓' if has_chrome else '✗'}")
        print(f"  - Languages set: {'✓' if 'zh-CN' in str(languages) else '⚠'}")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("\nClosing browser...")
            driver_manager.quit_driver()
            print("✓ Browser closed")

if __name__ == "__main__":
    test_anti_detection()

