import { useEffect, useState, type Dispatch, type SetStateAction } from "react";

type UseLocalStorageOptions<T> = {
  serializer?: (value: T) => string;
  deserializer?: (value: string) => T;
  initializeWithValue?: boolean;
};

export function useLocalStorage<T>(
  key: string,
  initialValue: T | (() => T),
  options: UseLocalStorageOptions<T> = {},
): [T, Dispatch<SetStateAction<T>>, () => void] {
  const {
    serializer = JSON.stringify,
    deserializer = JSON.parse,
    initializeWithValue = true,
  } = options;

  const [storedValue, setStoredValue] = useState<T>(() => {
    if (!initializeWithValue || typeof window === "undefined") {
      return typeof initialValue === "function"
        ? (initialValue as () => T)()
        : initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item
        ? deserializer(item)
        : typeof initialValue === "function"
          ? (initialValue as () => T)()
          : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return typeof initialValue === "function"
        ? (initialValue as () => T)()
        : initialValue;
    }
  });

  const setValue: Dispatch<SetStateAction<T>> = (value) => {
    try {
      const valueToStore =
        value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      if (typeof window !== "undefined") {
        window.localStorage.setItem(key, serializer(valueToStore));
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  };

  const remove = () => {
    try {
      if (typeof window !== "undefined") {
        window.localStorage.removeItem(key);
      }
      const valueToStore =
        typeof initialValue === "function"
          ? (initialValue as () => T)()
          : initialValue;
      setStoredValue(valueToStore);
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  };

  useEffect(() => {
    if (typeof window === "undefined") return;

    const handleStorageChange = (event: StorageEvent) => {
      if (event.key !== key) return;
      try {
        const item = event.newValue;
        if (item) {
          setStoredValue(deserializer(item));
        } else {
          const valueToStore =
            typeof initialValue === "function"
              ? (initialValue as () => T)()
              : initialValue;
          setStoredValue(valueToStore);
        }
      } catch (error) {
        console.warn(
          `Error reading localStorage key "${key}" on storage event:`,
          error,
        );
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [key, initialValue, deserializer]);

  return [storedValue, setValue, remove];
}
