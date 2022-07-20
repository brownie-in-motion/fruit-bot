from io import BytesIO
import re
import subprocess
import time

from PIL import Image
import cv2
import numpy as np
import pyautogui

import strategies

DIMENSIONS = (10, 17)


def screenshot():
    file = BytesIO(subprocess.check_output(['maim']))

    # return as numpy array without the alpha channel
    return np.array(
        Image.open(file)
    )[..., :3]


def ocr(array):
    file = BytesIO()
    image = Image.fromarray(
        ((array < 80) * 255).astype(np.uint8)
    )
    image.save(file, format='png')

    # run tesseract in single character mode
    result = subprocess.check_output(
        ['tesseract', '-', '-', '--psm', '6', 'digits'],
        input=file.getvalue(),
    )

    # extract the digit
    digit = re.search(r'\d', result.decode('utf-8'))

    if digit is None:
        image.save('ocr.png')
        print(result)

    assert digit is not None

    return int(digit[0])


def distance_to(image, color):
    # subtract #12cf70 out of the image
    gray = image.astype(np.int32)
    gray = gray - np.array(color)

    # find the magnitude of each pixel color
    gray = np.sum(gray ** 2, axis=2)
    gray = np.sqrt(gray)
    gray = np.clip(gray, 0, 255)
    return gray.astype(np.uint8)


def find_board():
    image = screenshot()

    gray = distance_to(image, (0x12, 0xcf, 0x70))

    blurred = cv2.GaussianBlur(gray, (13, 13), 0)
    binarized = (blurred < 60) * 255
    binarized = binarized.astype(np.uint8)

    contours, _ = cv2.findContours(
        binarized,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # find the second largest contour
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    assert len(contours) > 0

    rectangle = cv2.boundingRect(contours[0])
    return (rectangle[0], rectangle[1], rectangle[2], rectangle[3])


def finding_apples(left, top, width, height):
    image = screenshot()

    # crop the board
    image = image[top:top + height, left:left + width]

    gray = distance_to(image, (0xff, 0x66, 0x55))
    binarized = (gray < 60) * 255
    binarized = binarized.astype(np.uint8)

    # find the connected components
    contours, _ = cv2.findContours(
        binarized,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    assert len(contours) == DIMENSIONS[0] * DIMENSIONS[1]

    # draw the contours
    apples = []

    # get the average height
    total_height = 0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        crop_h = 1 / 8
        crop_w = 1 / 5
        cropped = gray[
            y + round(crop_h * h): y + round((1 - crop_h) * h),
            x + round(crop_w * w): x + round((1 - crop_w) * w)
        ]
        cropped = np.pad(cropped, 100, 'constant', constant_values=0)

        cropped = cv2.resize(cropped, (
            cropped.shape[1] * 2,
            cropped.shape[0] * 2
        ))

        pad = w // 4
        apples.append((
            (left + x - pad, top + y - pad),
            (left + x + w + pad, top + y + h + pad),
            cropped
        ))

        total_height += h

    average_height = total_height / len(contours)

    # slow sort the apples into rows
    apple_to_row = {}
    rows = []

    for apple in apples:
        coord, _, _ = apple
        for row in rows:
            if abs(coord[1] - row) < average_height // 2:
                apple_to_row[apple[0]] = row
                break
        else:
            rows.append(coord[1])
            apple_to_row[apple[0]] = coord[1]

    return sorted(
        apples,
        key=lambda apple: (
            apple_to_row[apple[0]],
            apple[0][0]
        )
    )


def label_apples(apples):
    buckets = []
    labels = []
    for _, _, image in apples:
        for bucket, digit in buckets:
            crop = image[:bucket.shape[0], :bucket.shape[1]]
            result = cv2.matchTemplate(crop, bucket, cv2.TM_CCOEFF_NORMED)
            _, val, _, _ = cv2.minMaxLoc(result)

            if val > 0.95:
                label = digit
                break
        else:
            label = ocr(image)
            buckets.append((image, label))

        labels.append(label)
    return labels


def shape(array):
    return [
        [
            array[row * DIMENSIONS[1] + col]
            for col in range(DIMENSIONS[1])
        ] for row in range(DIMENSIONS[0])
    ]


def main():
    print('finding board on screen...')
    left, top, width, height = find_board()

    print('starting game...')
    start_button = (left + width / 3, top + height / 2)
    pyautogui.click(start_button)
    pyautogui.moveTo(left, top)

    time.sleep(0.1)

    print('finding apples...')
    apples = finding_apples(left, top, width, height)

    print('labeling apples...')
    labels = label_apples(apples)

    label_grid = shape(labels)
    apple_grid = shape(apples)

    print('computing solution...')

    boxes = strategies.best_random(label_grid, 1000)

    print('executing moves...')

    def tween(_):
        return 1.0

    for (start_i, start_j), (end_i, end_j) in boxes:
        pyautogui.moveTo(
            apple_grid[start_i][start_j][0][0],
            apple_grid[start_i][start_j][0][1],
        )

        pyautogui.dragTo(
            apple_grid[end_i][end_j][1][0],
            apple_grid[end_i][end_j][1][1],
            0.15,
            tween,
        )


if __name__ == '__main__':
    main()
