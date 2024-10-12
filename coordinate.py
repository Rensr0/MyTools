import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import time
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)

# 用于保存矩形框的起始和结束点
start_point = None
end_point = None
drawing = False
screen_bgr = None  # 用于存储屏幕截图的BGR图像

# 鼠标回调函数，用于绘制矩形框
def draw_rectangle(event, x, y, flags, param):
    global start_point, end_point, drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        drawing = True
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        end_point = (x, y)
        drawing = False
        cv2.rectangle(screen_bgr, start_point, end_point, (0, 255, 0), 2)
        logging.info(f"矩形框坐标相对于截图左上角: {start_point} 到 {end_point}")

# 截取全屏
def capture_fullscreen():
    try:
        screen = pyautogui.screenshot()
        return np.array(screen)
    except Exception as e:
        logging.error(f"全屏截图失败: {e}")
        return None

# 根据标题查找窗口
def find_window_by_title(title):
    windows = gw.getWindowsWithTitle(title)
    if windows:
        return windows[0]
    logging.warning(f"未找到窗口: {title}")
    return None

# 激活指定标题的窗口
def activate_window(window):
    if window:
        try:
            logging.info(f"激活窗口: {window.title}")
            window.activate()
            time.sleep(0.5)  # 等待窗口激活
            if window.isMinimized:
                window.restore()  # 如果窗口被最小化，则还原
                time.sleep(0.5)  # 再次等待窗口还原
        except Exception as e:
            logging.error(f"激活窗口时出错: {e}")

# 截取指定窗口
def capture_window(window_title):
    window = find_window_by_title(window_title)
    activate_window(window)

    if window:
        x, y, width, height = window.left, window.top, window.width, window.height
        try:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            return np.array(screenshot), (x, y)
        except Exception as e:
            logging.error(f"窗口截图失败: {e}")
            return None, None
    return None, None

# 主程序
def main():
    global screen_bgr

    choice = input("选择操作: 1 - 全屏截图, 2 - 指定窗口截图\n请输入你的选择：")

    if choice == '1':
        screen_np = capture_fullscreen()
        if screen_np is None:
            print("全屏截图失败，程序将退出。")
            return
        screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
    elif choice == '2':
        window_title = input("请输入窗口标题（部分或完整）：")
        screen_np, position = capture_window(window_title)
        if screen_np is None or position is None:
            print("窗口截图失败，程序将退出。")
            return
        screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
    else:
        print("无效的选择！")
        return

    cv2.namedWindow("Screen Capture")
    cv2.setMouseCallback("Screen Capture", draw_rectangle, None)

    while True:
        cv2.imshow("Screen Capture", screen_bgr)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
