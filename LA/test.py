def create_boxes(values):
    boxes = []
    current_box = []
    total = 0

    for value in values:
        if total + value <= 10:
            current_box.append(value)
            total += value
        else:
            boxes.append(current_box)
            current_box = [value]
            total = value

    if current_box:
        boxes.append(current_box)

    return boxes

# Example usage
values = [2, 4, 3, 1, 5, 6]
boxes = create_boxes(values)
print(boxes)