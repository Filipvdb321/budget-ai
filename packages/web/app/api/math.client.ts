import { getSession } from "@auth0/nextjs-auth0";

const getMathToken = async (accessToken?: string) => {
    if (accessToken) {
        return accessToken;
    }

    const session = await getSession();
    if (!session || !session.accessToken) {
        throw new Error("Geen sessie gevonden");
    }
    return session.accessToken;
};

const mathApiFetch = async (
    path: string,
    options: RequestInit = {},
) => {
    // First get the token through our API route
    const tokenResponse = await fetch('/api/auth/token');
    if (!tokenResponse.ok) {
        throw new Error('Could not retrieve authentication token');
    }
    const { token } = await tokenResponse.json();

    const apiBaseUrl = process.env.NEXT_PUBLIC_MATH_API_URL || "http://localhost:5000";
    const apiUrl = `${apiBaseUrl}/${path}`;
    console.log(`Calling Math API: ${apiUrl}`);

    try {
        const response = await fetch(apiUrl, {
            ...options,
            headers: {
                ...options.headers,
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            mode: 'cors',
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Math API error! status: ${response.status}, message: ${errorText}`);
        }

        return response;
    } catch (error) {
        console.error(`Error calling math API ${apiUrl}:`, error);
        throw error;
    }
};

export const getPrediction = async (budgetId: string, daysAhead: number = 180) => {
    const response = await mathApiFetch(
        `balance-prediction/data?budget_id=${budgetId}&days_ahead=${daysAhead}`
    );
    return response.json();
};

export const getScheduledTransactions = async (budgetId: string) => {
    const response = await mathApiFetch(`sheduled-transactions?budget_id=${budgetId}`);
    return response.json();
};

export const suggestCategories = async (budgetId: string) => {
    const response = await mathApiFetch(
        `uncategorised-transactions/suggest-categories?budget_id=${budgetId}`
    );
    return response.json();
};

export const applyCategories = async (budgetId: string) => {
    const response = await mathApiFetch(
        `uncategorised-transactions/apply-categories?budget_id=${budgetId}`,
        { method: "POST" }
    );
    return response.json();
}; 