// Odoo JavaScript Framework Type Definitions
// This file helps VS Code understand Odoo's OWL and web framework

// Global Odoo namespace
declare global {
    var odoo: {
        define: (name: string, deps: string[], factory: Function) => void;
        ready: (callback: Function) => void;
        csrf_token: string;
        session_info: any;
    };
    
    var _: (text: string) => string;
    var _t: (text: string) => string;
    var $: any; // jQuery
    var owl: any;
    var luxon: any;
}

// OWL Framework
export interface Component {
    setup(): void;
    render(): any;
    mounted(): void;
    willUnmount(): void;
    willUpdateProps(nextProps: any): void;
    willPatch(): void;
    patched(): void;
    willDestroy(): void;
    env: any;
    props: any;
    state: any;
}

export interface ComponentClass {
    new (parent: any, props: any): Component;
    template: string;
    components: any;
    props: any;
}

// Odoo Web Framework Services
export interface RPC {
    (route: string, params?: any): Promise<any>;
}

export interface Notification {
    add(message: string, options?: any): void;
}

export interface ActionService {
    doAction(action: any, options?: any): Promise<any>;
}

export interface UserService {
    userId: number;
    userName: string;
    isAdmin: boolean;
    hasGroup(group: string): boolean;
}

export interface ORM {
    call(model: string, method: string, args?: any[], kwargs?: any): Promise<any>;
    create(model: string, vals: any[]): Promise<number[]>;
    read(model: string, ids: number[], fields?: string[]): Promise<any[]>;
    write(model: string, ids: number[], vals: any): Promise<boolean>;
    unlink(model: string, ids: number[]): Promise<boolean>;
    search(model: string, domain?: any[], options?: any): Promise<number[]>;
    searchRead(model: string, domain?: any[], fields?: string[], options?: any): Promise<any[]>;
}

// Odoo Field Widgets
export interface FieldWidget {
    name: string;
    value: any;
    readonly: boolean;
    required: boolean;
    invisible: boolean;
    record: any;
    field: any;
}

// Common Odoo Patterns
export function useState(initialState?: any): any;
export function useService(serviceName: string): any;
export function useRef(refName?: string): any;
export function useEffect(callback: Function, dependencies?: any[]): void;
export function onWillStart(callback: Function): void;
export function onMounted(callback: Function): void;
export function onWillUnmount(callback: Function): void;

// Odoo Web Client
export interface WebClient {
    action_manager: any;
    menu: any;
    notification: Notification;
}

// Common Odoo Utilities
export function formatDateTime(value: any): string;
export function formatDate(value: any): string;
export function formatFloat(value: number, precision?: number): string;
export function formatMonetary(value: number, currency?: any): string;
