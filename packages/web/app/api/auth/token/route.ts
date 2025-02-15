import { getSession } from "@auth0/nextjs-auth0";
import { NextResponse } from "next/server";

export async function GET() {
    try {
        const session = await getSession();
        if (!session || !session.accessToken) {
            return new NextResponse(
                JSON.stringify({ error: "Not authenticated" }),
                { 
                    status: 401,
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            );
        }

        return NextResponse.json({ 
            token: session.accessToken 
        }, {
            headers: {
                'Content-Type': 'application/json',
            }
        });
    } catch (error) {
        console.error("Error retrieving token:", error);
        return new NextResponse(
            JSON.stringify({ error: "Server error" }),
            { 
                status: 500,
                headers: {
                    'Content-Type': 'application/json',
                }
            }
        );
    }
} 