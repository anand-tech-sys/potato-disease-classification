import {Alert, Platform} from 'react-native';
import {
  check,
  PERMISSIONS,
  RESULTS,
  request,
  openSettings,
} from 'react-native-permissions';

export const isIOS = Platform.OS === 'ios';

function showAlert(msg) {
  Alert.alert('', msg, [
    {
      text: 'Cancel',
      onPress: () => console.log('Cancel Pressed'),
      style: 'cancel',
    },
    {
      text: 'Settings',
      onPress: () => {
        openSettings().catch(() => console.warn('cannot open settings'));
      },
    },
  ]);
}

const hasCameraPermission = async (withAlert = true) => {
  try {
    const permission = isIOS
      ? PERMISSIONS.IOS.CAMERA
      : PERMISSIONS.ANDROID.CAMERA;
    let status = await check(permission);
    if (status !== RESULTS.GRANTED) {
      status = await request(permission);
    }
    if (status === RESULTS.DENIED || status === RESULTS.BLOCKED) {
      if (withAlert) {
        showAlert(
          'Camera permission is required to take photos.',
        );
      }
      return false;
    }
    return true;
  } catch (error) {
    console.log(error);
    return false;
  }
};

const getPhotoPermission = () => {
  if (isIOS) {
    return PERMISSIONS.IOS.PHOTO_LIBRARY;
  }
  if (Number(Platform.Version) >= 33) {
    return PERMISSIONS.ANDROID.READ_MEDIA_IMAGES;
  }
  return PERMISSIONS.ANDROID.READ_EXTERNAL_STORAGE;
};

const hasPhotoPermission = async (withAlert = true) => {
  try {
    const permission = getPhotoPermission();
    let status = await check(permission);
    if (status !== RESULTS.GRANTED) {
      status = await request(permission);
    }
    if (status === RESULTS.DENIED || status === RESULTS.BLOCKED) {
      if (withAlert) {
        showAlert(
          'Photo library permission is required to select images.',
        );
      }
      return false;
    }
    return true;
  } catch (error) {
    console.log(error);
    return false;
  }
};

const PermissionsService = {
  hasCameraPermission,
  hasPhotoPermission,
};

export default PermissionsService;
