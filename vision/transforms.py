from torchvision import transforms

def preprocess(pil_image, size=256):
    """
    Takes an image and converts it to an ML ready tensor for eval
    :param size: resize amount
    :param pil_image: input scraped imaged
    :return: tensor ready for eval
    """

    resnet_transform = transforms.Compose([
        transforms.Resize((size, size)),  # or your target size
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    return resnet_transform(pil_image)