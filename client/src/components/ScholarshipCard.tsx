import type { ScholarshipResult } from "../types";

interface ScholarshipCardProps {
    result: ScholarshipResult;
}

export default function ScholarshipCard({ result }: ScholarshipCardProps) {
    return (
        <div className="border border-gray-200 rounded-xl p-5 bg-white shadow-sm max-w-xl">
            <h3 className="text-[#333E89] font-bold text-base mb-3">
                {result["Scholarship Name"]}
            </h3>
            <dl className="space-y-2 text-sm text-gray-700">
                <div className="flex gap-2">
                    <dt className="font-semibold shrink-0">Academic requirement:</dt>
                    <dd>{result["Minimum GWA"]}</dd>
                </div>
                <div className="flex gap-2">
                    <dt className="font-semibold shrink-0">Who can apply:</dt>
                    <dd>{result["Year Level restrictions"]}</dd>
                </div>
                <div className="flex gap-2">
                    <dt className="font-semibold shrink-0">Eligible programs:</dt>
                    <dd>{result["Specific Program"]}</dd>
                </div>
                <div className="flex gap-2">
                    <dt className="font-semibold shrink-0">Additional eligibility:</dt>
                    <dd>{result["Employment status preference"]}</dd>
                </div>
                <div className="flex gap-2">
                    <dt className="font-semibold shrink-0">Application deadline:</dt>
                    <dd>{result.Deadline}</dd>
                </div>
            </dl>
            <div className="mt-4">
                <p className="font-semibold text-sm text-gray-800 mb-2">Documents you may need</p>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                    {result["Required Documents"].map((doc, idx) => (
                        <li key={idx}>{doc}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
}