# TypeScript Advanced Types Guide

## Utility Types:
```typescript
// Partial - makes all properties optional
interface User {
    id: number;
    name: string;
    email: string;
}

type PartialUser = Partial<User>; // All properties optional

// Required - makes all properties required
type RequiredUser = Required<PartialUser>;

// Pick - selects specific properties
type UserPreview = Pick<User, 'id' | 'name'>;

// Omit - excludes specific properties
type UserWithoutId = Omit<User, 'id'>;

// Record - creates object with specific key/value types
type UserRoles = Record<string, string>;
```

## Conditional Types:
```typescript
type ApiResponse<T> = T extends string
    ? { message: T }
    : T extends number
    ? { count: T }
    : { data: T };

type StringResponse = ApiResponse<string>; // { message: string }
type NumberResponse = ApiResponse<number>; // { count: number }
```

## Mapped Types:
```typescript
// Make all properties optional
type Optional<T> = {
    [P in keyof T]?: T[P];
};

// Make all properties readonly
type Readonly<T> = {
    readonly [P in keyof T]: T[P];
};

// Add string prefix to all properties
type Prefixed<T, P extends string> = {
    [K in keyof T as `${P}${Capitalize<string & K>}`]: T[K];
};
```

## Template Literal Types:
```typescript
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type ApiEndpoint = `/api/${string}`;
type HttpUrl = `http${'s' | ''}://${string}`;

// Combining template literals
type ApiCall = `${HttpMethod} ${ApiEndpoint}`;
```

## Discriminated Unions:
```typescript
interface LoadingState {
    status: 'loading';
}

interface SuccessState {
    status: 'success';
    data: any;
}

interface ErrorState {
    status: 'error';
    error: string;
}

type State = LoadingState | SuccessState | ErrorState;

function handleState(state: State) {
    switch (state.status) {
        case 'loading':
            // TypeScript knows this is LoadingState
            break;
        case 'success':
            // TypeScript knows this is SuccessState
            console.log(state.data);
            break;
        case 'error':
            // TypeScript knows this is ErrorState
            console.log(state.error);
            break;
    }
}
```

## Type Guards:
```typescript
// Custom type guard
function isString(value: any): value is string {
    return typeof value === 'string';
}

// Using type guard
function processValue(value: string | number) {
    if (isString(value)) {
        // TypeScript knows value is string
        return value.toUpperCase();
    } else {
        // TypeScript knows value is number
        return value.toFixed(2);
    }
}

// instanceof type guard
class Dog {
    bark() { console.log('Woof!'); }
}

class Cat {
    meow() { console.log('Meow!'); }
}

function petSound(pet: Dog | Cat) {
    if (pet instanceof Dog) {
        pet.bark();
    } else {
        pet.meow();
    }
}
```

## Module System:
```typescript
// Named exports
export interface User {
    id: number;
    name: string;
}

export function createUser(name: string): User {
    return {
        id: Math.random(),
        name
    };
}

// Default export
export default class ApiClient {
    baseUrl: string;
    
    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }
}

// Import
import ApiClient, { User, createUser } from './api';
```