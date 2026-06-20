// TypeScript line comment
import { IFoo } from './foo';

/**
 * Interface documentation
 */
interface Person {
    name: string;
    age: number;
}

function greet(person: Person): string {
    // function comment
    return `Hello, ${person.name}`;
}

/* block comment */
const x: number = 1;
