import win32gui
import win32ui
import win32con
import win32api
import os

def capture_screenshot(filename='screenshot.bmp', output_path='C:\\WINDOWS\\Temp'):
    # Get handle to the desktop window
    hdesktop = win32gui.GetDesktopWindow()

    # Get the dimensions of the entire virtual screen (across monitors)
    width  = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left   = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top    = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    # Get device context of the desktop window
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)

    # Create a memory-based device context
    mem_dc = img_dc.CreateCompatibleDC()

    # Create a bitmap object
    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)

    mem_dc.SelectObject(screenshot)

    # Copy screen into memory DC
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)
    filepath = os.path.join(output_path, filename)

    # Save the screenshot
    screenshot.SaveBitmapFile(mem_dc, filepath)
    print(f"[+] Screenshot saved to: {filepath}")

    # Free resources
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())
    win32gui.ReleaseDC(hdesktop, desktop_dc)

# Example usage
if __name__ == '__main__':
    capture_screenshot()
