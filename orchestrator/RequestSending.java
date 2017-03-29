/*
RequestReceiving ONOS App by Jiakai Yu
 */

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class RequestSending {

    final static String url1 = "http://192.168.1.0:8080/TrafficRequest";
    final static String url2 = "http://192.168.2.0:8080/TrafficRequest";
    //final static String url1 = "http://192.168.0.1:8080/PCE/channel/set";
    //final static String url = "http://150.135.248.39:9090/PCE/channel/set";
    //final static String params = "{\"Source_Node\": \"2\", \"Destination_Node\": \"8\"}";


    //Set HTTP POST Method
    public static String post(String strURL, String params) {
        System.out.println(strURL);
        System.out.println(params);
        try {
            URL url = new URL(strURL);
            HttpURLConnection connection = (HttpURLConnection) url
                    .openConnection();
            connection.setDoOutput(true);
            connection.setDoInput(true);
            connection.setUseCaches(false);
            connection.setInstanceFollowRedirects(true);
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Accept", "application/json");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.connect();
            OutputStreamWriter out = new OutputStreamWriter(
                    connection.getOutputStream(), "UTF-8");
            out.append(params);
            out.flush();
            out.close();

            int length = (int) connection.getContentLength();
            InputStream is = connection.getInputStream();
            if (length != -1) {
                byte[] data = new byte[length];
                byte[] temp = new byte[512];
                int readLen = 0;
                int destPos = 0;
                while ((readLen = is.read(temp)) > 0) {
                    System.arraycopy(temp, 0, data, destPos, readLen);
                    destPos += readLen;
                }
                String result = new String(data, "UTF-8");
                System.out.println(result);
                return result;
            }
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return "error";
    }

    //Read request and split the request content into Source node, Destination node, Message ID, Request Class and so on
    public static String[] splitt(String str) {
        String strr = str.trim();
        String[] abc = strr.split("[\\p{Space}]+");
        String str1 = abc[0];
        String str2 = abc[1];
        String str3 = abc[2];
        String str4 = abc[3];
        String str5 = abc[4];
        System.out.println(str1);
        System.out.println(str2);
        System.out.println(str3);
        System.out.println(str4);
        System.out.println(str5);
        return abc;
    }

    //Based on the Source and Destination node pair to classify the request class as Crossdomain or Intradomain
    public static String rqst_idtf (String rqst[]) {
        String result = "no request";
        if (rqst[1].equals("add") && Integer.parseInt(rqst[2]) < 4 && Integer.parseInt(rqst[3]) > 3) {
            result = "CorssDomainRequest";
            //System.out.println(result);
            return result;
        }
        if (rqst[1].equals("add") && Integer.parseInt(rqst[3]) < 4 && Integer.parseInt(rqst[2]) > 3) {
            result = "CorssDomainRequest_rev";
            //System.out.println(result);
            return result;
        }
        if (rqst[1].equals("add") && Integer.parseInt(rqst[2]) < 4 && Integer.parseInt(rqst[3]) < 4) {
            //if (Integer.parseInt(rqst[2]) > Integer.parseInt(rqst[3]))
                //return "IntraDomainRequest_rev";
            result = "IntraDomainRequest";
            //System.out.println(result);
            return result;
        }
        if (rqst[1].equals("add") && Integer.parseInt(rqst[2]) > 3 && Integer.parseInt(rqst[3]) > 3) {
            //if (Integer.parseInt(rqst[2]) > Integer.parseInt(rqst[3]))
                //return "IntraDomainRequest_rev";
            result = "IntraDomainRequest_rev";
            //System.out.println(result);
            return result;
        }
        if (rqst[1].equals("tear") && Integer.parseInt(rqst[2]) < 4 && Integer.parseInt(rqst[3]) > 3) {
            result = "CrossDomainTearDown";
            //System.out.println(result);
            return result;
        }
        if (rqst[1].equals("tear") && Integer.parseInt(rqst[3]) < 4 && Integer.parseInt(rqst[2]) > 3) {
            result = "CrossDomainTearDown";
            //System.out.println(result);
            return result;
        }
        if (rqst[1].equals("tear") && Integer.parseInt(rqst[2]) < 4 && Integer.parseInt(rqst[3]) < 4) {
            //if (Integer.parseInt(rqst[2]) > Integer.parseInt(rqst[3]))
                //return "IntraDomainTearDown_rev";
            result = "IntraDomainTearDown";
            //System.out.println(result);
            return result;
        }
        if (rqst[1].equals("tear") && Integer.parseInt(rqst[2]) > 3 && Integer.parseInt(rqst[3]) > 3) {
            //if (Integer.parseInt(rqst[2]) > Integer.parseInt(rqst[3]))
                //return "IntraDomainTearDown_rev";
            result = "IntraDomainTearDown";
            //System.out.println(result);
            return result;
        }
        //System.out.println(result);
        return result;
    }


    public static void main(String[] args) {
        try {
            Scanner in = new Scanner(new File("/home/jk//Desktop/user_request.txt"));

            while (in.hasNextLine()) {
                String str = in.nextLine();
                String [] abc = splitt(str);
                String rqst_idtf = rqst_idtf(abc);
                System.out.println("The request is : " + rqst_idtf);
                String params = "{\"Msg_ID\": " + "\"" + abc[0] + "\"" + ", \"Source_Node\": " +  "\"" + abc[2] + "\"" + ", \"Destination_Node\": "  + "\"" +  abc[3] + "\"" +
                        ", \"Request_Class\": " + "\"" + rqst_idtf + "\"" + ", \"TearTraf\": " + "\"" + abc[4]  + "\"" + "}";// + ", \"Request_Class\":" + rqst_idtf + "}";
                post(url2, params);
                post(url1, params);

            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

    }

}
